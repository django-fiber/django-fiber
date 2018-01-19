import subprocess


def prereleaser_middle(data):
    """
    Custom code run when we make a release using Zest.releaser.

    It runs the unit tests one last time.
    """
    print('Running unit tests.')
    subprocess.check_output(['python', 'testproject/manage.py', 'test', 'fiber_test'])
