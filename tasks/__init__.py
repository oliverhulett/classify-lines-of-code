import os

from invoke import task

_HERE = os.path.abspath(os.path.dirname(__file__))
_PROJECT_DIR = os.path.dirname(_HERE)

@task
def venv(ctx):
    ctx.run('virtualenv "{}/.venv"'.format(_PROJECT_DIR))
    activate_this_file = '{}/.venv/bin/activate_this.py'.format(_PROJECT_DIR)
    execfile(activate_this_file, dict(__file__=activate_this_file))
    ctx.run('pip install {}'.format(' '.join([
        'pytest',
    ])))

@task(pre=(venv,))
def tests(ctx):
    ctx.run('PYTHONPATH="{}/src" pytest tests'.format(_PROJECT_DIR))
