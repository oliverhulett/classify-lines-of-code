import os

from invoke import task

_PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))


@task
def venv(ctx):
    activate_this_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "activate_this.py")
    if not os.path.exists(activate_this_file):
        ctx.run('/bin/bash "{}/init.sh"'.format(_PROJECT_DIR))
    try:
        execfile(activate_this_file, dict(__file__=activate_this_file))  # NOQA
    except:
        exec (open(activate_this_file).read())


@task(pre=(venv,))
def tests(ctx, quiet=False, junit=None):
    ctx.run(
        'pytest {args} {}/tests'.format(
            _PROJECT_DIR,
            args=' '.join([
                '--verbose' if not quiet else '',
                '--junitxml={}'.format(junit) if junit is not None else '',
            ])
        )
    )


@task
def format(ctx):
    ctx.run('"{}/format.sh"'.format(_PROJECT_DIR))


@task(pre=(tests,))
def package(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        for cmd in (
                'check',
                'build',
                'sdist',
                'bdist',
        ):
            ctx.run('./setup.py {}'.format(cmd))


@task(pre=(package,))
def install(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        ctx.run('pip uninstall --yes cloc', warn=True)
        ctx.run('pip install .')


@task(pre=(
    format,
    tests,
    install,
))
def all(ctx):
    pass


@task
def develop(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        ctx.run('pip uninstall --yes cloc', warn=True)
        ctx.run('pip install -e .')


@task
def clean(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        for d in (
                '.cache',
                '.pytest_cache',
                '.venv',
                'build',
                'dist',
                'src/*/*.pyc',
                'src/cloc.egg-info',
                'tests/*.pyc',
                'tests/cloc/__pycache__',
        ):
            ctx.run('rm -rf "{}"'.format(d), warn=True)


class WorkingDirectory(object):
    def __init__(self, wd):
        self.old_wd = os.getcwd()
        self.new_wd = wd

    def __enter__(self):
        os.chdir(self.new_wd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_wd)
