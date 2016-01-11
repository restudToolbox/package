#!/usr/bin/env python
""" This script cleans the directories.
"""

# standard library
import shutil
import glob
import os

''' Auxiliary functions
'''


def cleanup(all_=True):
    """ Cleanup during development.
    """
    SAVE_FILES = ['create', 'clean', 'acropolis.pbs', 'modules', 'clean.py',
                  'create.py', 'auxiliary.py', 'update', 'update.py',
                  'graphs', 'graphs.py', 'aggregate', 'aggregate.py']

    for name in glob.glob('*'):
        if name in SAVE_FILES:
            pass
        else:
            remove(name)


def remove(names):
    """ Remove files or directories.
    """
    if not isinstance(names, list):
        names = [names]

    for name in names:
        try:
            os.remove(name)
        except IsADirectoryError:
            shutil.rmtree(name)

''' Main
'''
if __name__ =='__main__':

    root_dir = os.getcwd()

    for subdir, _, _ in os.walk('.'):

        os.chdir(subdir)
        cleanup()
        os.chdir(root_dir)
