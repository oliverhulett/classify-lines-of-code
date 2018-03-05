import os

from invoke import task

_HERE = os.path.abspath(os.path.dirname(__file__))
_PROJECT_DIR = os.path.dirname(_HERE)

@task
def venv(ctx):
    activate_this_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "activate_this.py")
    if not os.path.exists(activate_this_file):
        ctx.run('/bin/bash "{}/init.sh"'.format(_PROJECT_DIR))
    execfile(activate_this_file, dict(__file__=activate_this_file))

@task(pre=(venv,))
def tests(ctx, quiet=False, junit=None):
    ctx.run('pytest {args} {}/tests'.format(_PROJECT_DIR, args=' '.join([
        '--verbose' if not quiet else '',
        '--junitxml={}'.format(junit) if junit is not None else '',
    ])))

@task(pre=(tests,))
def package(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        for cmd in ('check', 'build', 'sdist', 'bdist',):
            ctx.run('./setup.py {}'.format(cmd))

@task(pre=(package,))
def install(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        ctx.run('pip install .')

@task
def clean(ctx):
    with WorkingDirectory(_PROJECT_DIR):
        for d in (
            '.cache',
            '.pytest_cache',
            '.venv',
            'src/cloc.egg-info',
            'tests/cloc/__pycache__',
            'src/*/*.pyc',
            'tests/*.pyc',
        ):
            ctx.run('rm -rf "{}"'.format(d))

class WorkingDirectory(object):
    def __init__(self, wd):
        self.old_wd = os.getcwd()
        self.new_wd = wd

    def __enter__(self):
        os.chdir(self.new_wd)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.old_wd)
