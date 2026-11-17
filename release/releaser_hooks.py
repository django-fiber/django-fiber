import subprocess
import sys


def prereleaser_middle(data):
    """
    Custom code run when we make a release using Zest.releaser.

    It runs the unit tests one last time.
    """
    print('Running unit tests.')
    subprocess.check_output([sys.executable, 'testproject/manage.py', 'test', 'fiber_test'])
