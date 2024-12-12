import os

from tome.internal.utils.files import chdir
from tome.internal.utils.files import save_files
from tests.utils.runners import check_output_runner

from tests.utils.files import temp_folder


def git_create_bare_repo(folder=None, reponame="repo.git"):
    folder = folder or temp_folder()
    cwd = os.getcwd()
    try:
        os.chdir(folder)
        check_output_runner(f'git init --bare {reponame}')
        return os.path.join(folder, reponame).replace("\\", "/")
    finally:
        os.chdir(cwd)


def create_local_git_repo(
    files=None, branch=None, submodules=None, folder=None, commits=1, tags=None, origin_url=None, main_branch="main"
):
    tmp = folder or temp_folder()
    if files:
        save_files(tmp, files)

    def _run(cmd, p):
        with chdir(p):
            return check_output_runner(f"git {cmd}").strip()

    _run("init .", tmp)
    _run('config user.name "Your Name"', tmp)
    _run('config user.email "you@example.com"', tmp)
    _run(f"checkout -b {branch or main_branch}", tmp)

    _run("add .", tmp)
    for _ in range(0, commits):
        _run('commit --allow-empty -m "commiting"', tmp)

    tags = tags or []
    for tag in tags:
        _run("tag %s" % tag, tmp)

    if submodules:
        for submodule in submodules:
            _run('submodule add "%s"' % submodule, tmp)
        _run('commit -m "add submodules"', tmp)

    if origin_url:
        _run(f'remote add origin {origin_url}', tmp)

    commit = _run('rev-list HEAD -n 1', tmp)
    return tmp.replace("\\", "/"), commit


def git_add_changes_commit(folder, msg="fix"):
    cwd = os.getcwd()
    try:
        os.chdir(folder)
        # Make sure user and email exist, otherwise it can error
        check_output_runner('git config user.name "Your Name"')
        check_output_runner('git config user.email "you@example.com"')
        check_output_runner('git add .')
        check_output_runner(f'git commit -m "{msg}"')
        return check_output_runner("git rev-parse HEAD").strip()
    finally:
        os.chdir(cwd)
