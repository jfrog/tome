from enum import Enum
import os
import base64
import getpass
from sqlalchemy import create_engine, MetaData, LargeBinary, String, Integer
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, Session
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.fernet import Fernet, InvalidToken
from tome.errors import TomeException

State = Enum('State', ['Unmodified', 'Created', 'Updated'])


class VaultApi:
    def __init__(self, cache_folder):
        self.cache_folder = cache_folder
        self.vaults_folder = os.path.join(self.cache_folder, 'vault')
        if not os.path.exists(self.vaults_folder):
            os.makedirs(self.vaults_folder, exist_ok=True)

    def open(self, name='default', password=None):
        if password is None:
            password = getpass.getpass(f"Enter password for vault '{name}': ")

        if name not in self.vaults:
            raise TomeException(f"Vault '{name}' does not exist. Please run 'tome vault create' to create it first.")

        vault_path = f"sqlite:///{os.path.join(self.vaults_folder, f'{name}-vault.db')}"
        with Session(create_engine(vault_path)) as session:
            key = self._create_token(
                session.query(TomeInternal).filter(TomeInternal.key == 'salt').first().value,
                password,
            )
            try:
                vault_key = key.decrypt(
                    session.query(TomeInternal).filter(TomeInternal.key == 'vault_key').first().value
                )
            except InvalidToken:
                raise TomeException(f"Unable to open vault '{name}'. Incorrect password.")
            return Vault(key=Fernet(vault_key), vault_path=vault_path)

    def create(self, name, password):
        name = name.replace(' ', '')
        if os.path.exists(os.path.join(self.vaults_folder, f'{name}-vault.db')):
            raise TomeException(f"Vault {name} already exists")
        engine = create_engine(f"sqlite:///{os.path.join(self.vaults_folder, f'{name}-vault.db')}")
        Base.metadata.create_all(engine)
        with Session(engine) as session:
            salt = os.urandom(16)
            create_instance(session, TomeInternal, {'key': 'salt', 'value': salt})
            master_key = self._create_token(salt, password)
            create_instance(
                session, TomeInternal, {'key': 'vault_key', 'value': master_key.encrypt(Fernet.generate_key())}
            )

    def delete(self, name, password):
        vault = self.open(name, password)
        vault.clean()
        vault.close()
        os.remove(os.path.join(self.vaults_folder, f'{name}-vault.db'))

    @staticmethod
    def _create_token(salt, password):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        token = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(token)

    @property
    def vaults(self):
        return {
            f.replace('-vault.db', ''): os.path.join(self.vaults_folder, f)
            for f in os.listdir(self.vaults_folder)
            if (os.path.isfile(os.path.join(self.vaults_folder, f)) and '-vault.db' in f)
        }

    def list(self):
        result = {}
        for name, db_path in self.vaults.items():
            with Session(create_engine(f"sqlite:///{db_path}")) as session:
                secrets = session.query(SecretText).all()
            result[name] = [(secret.key, secret.description) for secret in secrets]
        return result


class Vault:
    def __init__(self, key, vault_path):
        self.engine = create_engine(vault_path)
        self.key = key

    def close(self):
        self.key = None
        Session(self.engine).close_all()

    def _decrypt(self, value):
        try:
            return self.key.decrypt(value).decode()
        except InvalidToken:
            raise TomeException('Invalid password')

    def list(self):
        with Session(self.engine) as session:
            secrets = session.query(SecretText).all()
            return [(secret.key, secret.description) for secret in secrets]

    def read(self, name):
        with Session(self.engine) as session:
            secret = session.query(SecretText).filter(SecretText.key == name).first()
            if secret:
                return self._decrypt(secret.text)

    def create(self, name, text, description=None, update=False):
        with Session(self.engine) as session:
            secret = session.query(SecretText).filter(SecretText.key == name).first()
            if secret:
                if update:
                    self._decrypt(secret.text)
                    text = self.key.encrypt(text.encode())
                    timestamp = self.key.extract_timestamp(text)
                    secret.text = text
                    secret.timestamp = timestamp
                    secret.description = description or secret.description
                    commit_and_refresh(session, secret)
                    return State.Updated
                return State.Unmodified
            else:
                text = self.key.encrypt(text.encode())
                timestamp = self.key.extract_timestamp(text)
                secret = create_instance(
                    session,
                    SecretText,
                    {'key': name, 'text': text, 'timestamp': timestamp, 'description': description},
                )
                return State.Created

    def delete(self, name):
        with Session(self.engine) as session:
            secret = session.query(SecretText).filter(SecretText.key == name).first()
            if secret:
                self._decrypt(secret.text)
                session.delete(secret)
                session.commit()

    def clean(self):
        metadata_obj = MetaData()
        metadata_obj.drop_all(self.engine)


def create_instance(session, secret_instance, fields):
    secret_instance = secret_instance(**fields)
    session.add(secret_instance)
    return commit_and_refresh(session, secret_instance)


def commit_and_refresh(session, secret_instance):
    session.commit()
    session.refresh(secret_instance)
    return secret_instance


class Base(DeclarativeBase):
    pass


class SecretText(Base):
    __tablename__ = "secret_text"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    text: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)


class TomeInternal(Base):
    __tablename__ = "tome_internal"
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    value: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
