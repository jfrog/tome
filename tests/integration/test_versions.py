import textwrap

from tests.utils.scm import git_create_bare_repo, git_add_changes_commit
from tests.utils.tools import TestClient


def test_install_from_git():
    url = git_create_bare_repo()
    c = TestClient()
    c.run_command(f'git clone "{url}" myclone')
    hello = textwrap.dedent('''\
       from tome.command import tome_command

       @tome_command()
       def hello(tome_api, parser, *args):
           """hello tome."""
           print(f"hello: {}!!")
       ''')
    with c.chdir("myclone"):
        c.save({"hello/hello.py": hello.format("v1")})
        commit1 = git_add_changes_commit(c.current_folder)
        c.run_command("git push")
        c.save({"hello/hello.py": hello.format("v2")})
        c.run_command("git checkout -b branchv2")
        commit2 = git_add_changes_commit(c.current_folder)
        c.run_command("git push --set-upstream origin branchv2")

    c.run(f"install '{url}'")
    c.run("info hello:hello")
    assert f"commit: {commit1}" in c.out
    assert "version:" not in c.out
    c.run("hello:hello")
    assert "hello: v1!!" in c.out

    c.run(f"install '{url}@branchv2'")
    c.run("info hello:hello")
    assert f"commit: {commit2}" in c.out
    assert "version: branchv2" in c.out
    c.run("hello:hello")
    assert "hello: v2!!" in c.out
