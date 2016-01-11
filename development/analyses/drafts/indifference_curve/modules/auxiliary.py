""" Module with some auxiliary methods for the analysis of model
misspecification.
"""

# standard library
from scipy.interpolate import interp1d

import matplotlib.pylab as plt
import matplotlib

import pickle as pkl
import numpy as np
import shlex
import glob


import shutil
import shlex
import glob
import os

# project library

from robupy.tests.random_init import print_random_dict
from robupy.clsRobupy import RobupyCls
from robupy import solve

# module wide variables
SCALING = 100000.00


def plot_model_misspecification(yvalues, xvalues):
    """ Plot the results from the model misspecification exercise.
    """

    # Set up interpolation
    f = interp1d(xvalues, yvalues, kind='quadratic')
    x_new = np.linspace(0.00, 0.02, num=41, endpoint=True)

    # Initialize canvas and basic plot.
    ax = plt.figure(figsize=(12, 8)).add_subplot(111)
    ax.plot(x_new, f(x_new), '-k', color='red', linewidth=5)

    # Both axes
    ax.tick_params(labelsize=18, direction='out', axis='both', top='off',
            right='off')

    # X axis
    ax.set_xlim([0.00, 0.02])
    ax.set_xlabel('Level of Ambiguity', fontsize=16)
    ax.set_xticklabels(('Absent', 'Low', 'High'))
    ax.set_xticks((0.00, 0.01, 0.02))

    # Y axis
    ax.set_ylabel('Intercept', fontsize=16)
    ax.yaxis.get_major_ticks()[0].set_visible(False)

    # Formatting with comma for thousands.
    func = matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ','))
    ax.get_yaxis().set_major_formatter(func)

    plt.savefig('rslts/model_misspecification.png', bbox_inches='tight',
                format='png')


def distribute_arguments(parser):
    """ Distribute command line arguments.
    """
    # Process command line arguments
    args = parser.parse_args()

    # Extract arguments
    is_recompile = args.is_recompile
    num_procs = args.num_procs
    is_debug = args.is_debug
    level = args.level
    grid = args.grid

    # Check arguments
    assert (isinstance(level, float))
    assert (level >= 0.00)
    assert (is_recompile in [True, False])
    assert (is_debug in [True, False])
    assert (isinstance(num_procs, int))
    assert (num_procs > 0)

    # Check and process information about grid.
    assert (len(grid) == 3)
    grid = float(grid[0]), float(grid[1]), int(grid[2])

    # Finishing
    return level, grid, num_procs, is_recompile, is_debug


def solve_true_economy(init_dict, is_debug):
    """ Solve and store true economy.
    """
    # Prepare directory structure
    os.mkdir('true'), os.chdir('true')
    # Modify initialization dictionary
    if is_debug:
        init_dict['BASICS']['periods'] = 5
    # Solve economy
    solve(_get_robupy_obj(init_dict))
    # Get baseline choice distributions
    base_choices = get_period_choices()
    # Store material required for restarting an estimation run
    print_random_dict(init_dict)
    # Return to root directory
    os.chdir('../')
    # Finishing
    return base_choices


def criterion_function(init_dict, base_choices):
    """ Get the baseline distribution.
    """
    # Solve requested model
    solve(_get_robupy_obj(init_dict))
    # Get choice probabilities
    alternative_choices = get_period_choices()
    # Calculate squared mean-deviation of all transition probabilities
    rslt = np.mean(np.sum((base_choices[:, :] - alternative_choices[:, :])**2))
    # Finishing
    return rslt


def get_period_choices():
    """ Return the share of agents taking a particular decision in each
        of the states for all periods.
    """
    # Auxiliary objects
    file_name, choices = 'data.robupy.info', []
    # Process file
    with open(file_name, 'r') as output_file:
        for line in output_file.readlines():
            # Split lines
            list_ = shlex.split(line)
            # Skip empty lines
            if not list_:
                continue
            # Check if period
            try:
                int(list_[0])
            except ValueError:
                continue
            # Extract information about period decisions
            choices.append([float(x) for x in list_[1:]])
    # Type conversion
    choices = np.array(choices)
    # Finishing
    return choices


def _get_robupy_obj(init_dict):
    """ Get the object to pass in the solution method.
    """
    # Initialize and process class
    robupy_obj = RobupyCls()
    robupy_obj.set_attr('init_dict', init_dict)
    robupy_obj.lock()
    # Finishing
    return robupy_obj


def get_float_directories():
    """ Get directories that have a float-type name.
    """
    # Get all possible files.
    candidates = glob.glob('*')
    directories = []
    for candidate in candidates:
        # Check if directory at all.
        if not os.path.isdir(candidate):
            continue
        # Check if directory with float-type name.
        try:
            float(candidate)
        except ValueError:
            continue
        # Collect survivors.
        directories += [float(candidate)]
    # Finishing
    return directories


def get_name(float_):
    """ Construct directory label from float.
    """
    return '%03.3f' % float_


def get_criterion_function():
    """ Process get value of criterion function.
    """
    with open('misspecification.robupy.log', 'r') as output_file:
        for line in output_file.readlines():
            # Split lines
            list_ = shlex.split(line)
            # Skip all irrelevant lines.
            if not len(list_) == 2:
                continue
            if not list_[0] == 'Criterion':
                continue
            # Finishing
            return float(list_[1])


