import os

from invoke import task, call

_PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
_src_dirs = []
_test_dirs = []
_deduping = {}


def _discover(ctx):
    if 'discover' in _deduping:
        return
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


def _venv(ctx):
    if 'venv' in _deduping:
        return
    activate_this_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "activate_this.py")
    if not os.path.exists(activate_this_file):
        ctx.run('/bin/bash "{}/init.sh"'.format(_PROJECT_DIR))
    execfile(activate_this_file, dict(__file__=activate_this_file))  # NOQA


@task
def format(ctx):
    _discover(ctx)
    _venv(ctx)
    ctx.run('"{}/format.sh"'.format(_PROJECT_DIR))


@task
def check(ctx):
    _discover(ctx)
    _venv(ctx)
    pychecker_file = os.path.join(_PROJECT_DIR, ".venv", "bin", "pychecker")
    if not os.path.exists(pychecker_file):
        ctx.run(
            'pip install https://sourceforge.net/projects/pychecker/files/pychecker/0.8.19/pychecker-0.8.19.tar.gz/download'
        )
    with ctx.cd(_PROJECT_DIR):
        ctx.run(
            'pychecker --stdlib --import --limit 100 {}'.format(
                ' '.join([os.path.join(sd, '*.py') for sd in _src_dirs])
            )
        )


@task
def develop(ctx):
    _discover(ctx)
    _venv(ctx)
    ctx.run('pip uninstall --yes cloc', warn=True)
    with ctx.cd(_PROJECT_DIR):
        ctx.run('pip install -e .')


@task(pre=(develop,))
def tests(ctx, quiet=False):
    _discover(ctx)
    _venv(ctx)
    for dirname in _test_dirs:
        with ctx.cd(os.path.join(_PROJECT_DIR, dirname)):
            ctx.run('python -m unittest2 {}'.format('--verbose' if not quiet else '--fail-fast'))


def _coverage(ctx):
    _discover(ctx)
    _venv(ctx)
    develop(ctx)
    for dirname in _test_dirs:
        td = os.path.join(_PROJECT_DIR, dirname)
        with ctx.cd(td):
            ctx.run(
                'coverage run --source={} -m unittest2'.format(
                    ','.join([os.path.relpath(os.path.join(_PROJECT_DIR, s), td) for s in _src_dirs])
                )
            )
    with ctx.cd(os.path.join(_PROJECT_DIR)):
        ctx.run('coverage combine {}'.format(' '.join([os.path.join(td, '.coverage') for td in _test_dirs])))


@task
def coverage_report(ctx, annotate=False, html=False, xml=False):
    _discover(ctx)
    _venv(ctx)
    _coverage(ctx)
    with ctx.cd(os.path.join(_PROJECT_DIR)):
        ctx.run('coverage report')
        if annotate:
            ctx.run('coverage annotate --directory=coverage/annotated')
        if html:
            ctx.run('coverage html --directory=coverage/htmlcov')
        if xml:
            ctx.run('coverage xml -o coverage/coverage.xml')


@task(post=(coverage_report,))
def coverage(ctx):
    pass


@task(pre=(tests,))
def package(ctx, verbose=False, quiet=False):
    _venv(ctx)
    with ctx.cd(_PROJECT_DIR):
        for cmd in (
                'check',
                'build',
                'sdist',
                'bdist',
        ):
            ctx.run('./setup.py {} {} {}'.format('--verbose' if verbose else '', '--quiet' if quiet else '', cmd))


@task(pre=(call(package, quiet=True),))
def install(ctx):
    _venv(ctx)
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
    call(coverage_report, annotate=True, html=True, xml=True),
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
