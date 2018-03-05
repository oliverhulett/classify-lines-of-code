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
def tests(ctx):
    ctx.run('pytest tests')

@task
def clean(ctx):
    ctx.run('rm -rf .cache .pytest_cache .venv src/cloc.egg-info tests/cloc/__pycache__ src/*/*.pyc tests/*.pyc')
