#!/usr/bin/env python
""" Script that executes the testings for the Travis CI integration server.
"""

# standard library
import os

# Get current directory.
CURRENT_DIR = os.getcwd()

# Get directory of ROBUPY package.
ROBUPY_DIR = os.path.abspath(os.path.dirname(__file__))
ROBUPY_DIR = ROBUPY_DIR.replace('/travis-ci', '/robupy')

# Compile the package as possible.
os.system('echo $HOSTNAME')

os.system('ln -sf /home/travis/virtualenv/python3.4.2/bin/f2py /home/travis/virtualenv/python3.4.2/bin/f2py3')


os.chdir(ROBUPY_DIR)
os.system('./waf configure build --fortran --debug')
os.chdir(CURRENT_DIR)
    
os.system('f2py')
os.system('f2py3')


os.system('which f2py')
os.system('which f2py3')




# Tests
os.system('nosetests --with-coverage --cover-package=robupy --exe')

os.system('coveralls')
