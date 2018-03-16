import os

from invoke import task

_PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
_src_dirs = []
_test_dirs = []


@task
def _discover(ctx):
    global _src_dirs
    global _test_dirs
    with ctx.cd(_PROJECT_DIR):
        _src_dirs = [
            x for x in ctx.run('git ls-files -z src | xargs -0n 1 dirname | sort -u', hide='both', echo=False)
            .stdout.split() if os.path.exists(os.path.join(x, '__init__.py'))
        ]
        _test_dirs = ctx.run(
            'git ls-files -z tests | xargs -0n 1 dirname | sort -u', hide='both', echo=False
        ).stdout.split()


@task
def develop(ctx):
    ctx.run('pip uninstall --yes cloc', warn=True)
    with ctx.cd(_PROJECT_DIR):
        ctx.run('pip install -e .')


@task(post=(develop,))
def _venv(ctx):
    activate_this_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "activate_this.py")
    if not os.path.exists(activate_this_file):
        ctx.run('/bin/bash "{}/init.sh"'.format(_PROJECT_DIR))
    execfile(activate_this_file, dict(__file__=activate_this_file))  # NOQA


@task(pre=(
    _discover,
    _venv,
))
def tests(ctx, quiet=False):
    for dirname in _test_dirs:
        with ctx.cd(os.path.join(_PROJECT_DIR, dirname)):
            ctx.run('unit2 {}'.format('--verbose' if not quiet else '--fail-fast'))


@task
def format(ctx):
    ctx.run('"{}/format.sh"'.format(_PROJECT_DIR))


@task(pre=(
    _discover,
    _venv,
))
def check(ctx):
    pychecker_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "pychecker")
    if not os.path.exists(pychecker_file):
        ctx.run(
            'pip install https://sourceforge.net/projects/pychecker/files/pychecker/0.8.19/pychecker-0.8.19.tar.gz/download'
        )
    with ctx.cd(_PROJECT_DIR):
        ctx.run('pychecker --config "{}" {}'.format('.pycheckrc', ' '.join(_src_dirs)))


@task(pre=(
    _venv,
    tests,
))
def package(ctx):
    with ctx.cd(_PROJECT_DIR):
        for cmd in (
                'check',
                'build',
                'sdist',
                'bdist',
        ):
            ctx.run('./setup.py {}'.format(cmd))


@task(pre=(
    _venv,
    package,
))
def install(ctx):
    ctx.run('pip uninstall --yes cloc', warn=True)
    with ctx.cd(_PROJECT_DIR):
        ctx.run('pip install .')


@task
def uninstall(ctx):
    ctx.run('pip uninstall --yes cloc', warn=True)


@task(pre=(
    format,
    check,
    tests,
    install,
))
def all(ctx):
    pass


@task
def clean(ctx):
    with ctx.cd(_PROJECT_DIR):
        for d in (
                '.venv',
                'build',
                'dist',
                'src/*/*.pyc',
                'src/cloc.egg-info',
                'tests/*/*.pyc',
        ):
            ctx.run('rm -rf "{}"'.format(d), warn=True)
