""" This module contains auxiliary functions for the PYTEST suite.
"""
import pandas as pd
import numpy as np

import shlex

from respy.python.solve.solve_auxiliary import pyth_create_state_space
from respy.python.shared.shared_auxiliary import dist_class_attributes
from respy.python.shared.shared_constants import DATA_FORMATS_SIM
from respy.python.shared.shared_constants import DATA_LABELS_SIM
from respy.python.shared.shared_constants import DATA_LABELS_EST
from respy.python.simulate.simulate_auxiliary import write_out
from respy.python.shared.shared_constants import OPT_AMB_FORT
from respy.python.shared.shared_constants import OPT_AMB_PYTH
from respy.python.shared.shared_constants import OPT_EST_FORT
from respy.python.shared.shared_constants import OPT_EST_PYTH

from respy import RespyCls
from respy import simulate

# module-wide variables
OPTIMIZERS_EST = OPT_EST_FORT + OPT_EST_PYTH
OPTIMIZERS_AMB = OPT_AMB_FORT + OPT_AMB_PYTH


def simulate_observed(respy_obj, is_missings=True):
    """ This function addes two important features of observed datasests: (1)
    missing observations and missing wage information.
    """
    def drop_agents_obs(group, num_drop):
        """ We drop a random number of observations for each agent.
        """
        group.set_index('Period', drop=False, inplace=True)
        indices = np.random.choice(group.index, num_drop, replace=False)
        group.drop(indices, inplace=True)
        return group

    num_periods = respy_obj.get_attr('num_periods')
    seed_sim = respy_obj.get_attr('seed_sim')

    simulate(respy_obj)

    # It is important to set the seed after the simulation call. Otherwise,
    # the value of the seed differs due to the different implementations of
    # the PYTHON and FORTRAN programs.
    np.random.seed(seed_sim)

    if is_missings:
        share = np.random.uniform(high=0.9, size=1)
        share_missing_obs = np.random.choice([0, share])

        share = np.random.uniform(high=0.9, size=1)
        share_missing_wages = np.random.choice([0, share])
    else:
        share_missing_wages = 0
        share_missing_obs = 0

    # We want to drop random observations by agents. This mimics the frequent
    # empirical fact that we loose track of agents (at least temporarily).
    data_frame = pd.read_csv('data.respy.dat', delim_whitespace=True, header=0,
        na_values='.', dtype=DATA_FORMATS_SIM, names=DATA_LABELS_SIM)

    if share_missing_obs != 0:
        num_drop_obs = int(num_periods * share_missing_obs)
    else:
        num_drop_obs = 0

    data_subset = data_frame.groupby('Identifier').apply(drop_agents_obs,
        num_drop=num_drop_obs)

    # We also want to drop the some wage observations.
    is_working = data_subset['Choice'].isin([1, 2])
    num_drop_wages = int(np.sum(is_working) * share_missing_wages)

    # As a special case, we might be dealing with a dataset where not one is
    # working anyway.
    if num_drop_wages > 0:
        indices = data_subset['Wage'][is_working].index
        index_missing = np.random.choice(indices, num_drop_wages, False)
        data_subset.loc[index_missing, 'Wage'] = None
    else:
        pass

    # We can restrict the information to observed entities only.
    data_frame = data_frame[DATA_LABELS_EST]

    write_out(respy_obj, data_subset)

    return respy_obj


def compare_est_log(base_est_log):
    """ This function is required as the log files can be slightly different
    for good reasons. The error capturing of an IndexError is required as
    sometimes the ...
    """

    for _ in range(25):

        try:

            with open('est.respy.log') as in_file:
                alt_est_log = in_file.readlines()

            for j, _ in enumerate(alt_est_log):
                alt_line, base_line = alt_est_log[j], base_est_log[j]
                list_ = shlex.split(alt_line)

                if not list_:
                    continue

                if list_[0] in ['Criterion']:
                    alt_val = float(shlex.split(alt_line)[1])
                    base_val = float(shlex.split(base_line)[1])
                    np.testing.assert_almost_equal(alt_val, base_val)
                elif list_[0] in ['Ambiguity']:
                    # We know that the results from the worst-case
                    # determination are very sensitive for ill-conditioned
                    # problems and thus the performance varies across versions.
                    pass
                elif list_[0] in ['Time', 'Duration']:
                    pass
                else:
                    assert alt_line == base_line

            return

        except IndexError:
            pass


def write_interpolation_grid(file_name):
    """ Write out an interpolation grid that can be used across
    implementations.
    """
    # Process relevant initialization file
    respy_obj = RespyCls(file_name)

    # Distribute class attribute
    num_periods, num_points_interp, edu_start, edu_max, min_idx = \
        dist_class_attributes(respy_obj,
            'num_periods', 'num_points_interp', 'edu_start', 'edu_max', 'min_idx')

    # Determine maximum number of states
    _, states_number_period, _, max_states_period = \
        pyth_create_state_space(num_periods, edu_start, edu_max, min_idx)

    # Initialize container
    booleans = np.tile(True, (max_states_period, num_periods))

    # Iterate over all periods
    for period in range(num_periods):

        # Construct auxiliary objects
        num_states = states_number_period[period]
        any_interpolation = (num_states - num_points_interp) > 0

        # Check applicability
        if not any_interpolation:
            continue

        # Draw points for interpolation
        indicators = np.random.choice(range(num_states),
            size=(num_states - num_points_interp), replace=False)

        # Replace indicators
        for i in range(num_states):
            if i in indicators:
                booleans[i, period] = False

    # Write out to file
    np.savetxt('interpolation.txt', booleans, fmt='%s')

    # Some information that is useful elsewhere.
    return max_states_period


def write_draws(num_periods, max_draws):
    """ Write out draws to potentially align the different implementations of
    the model. Note that num draws has to be less or equal to the largest
    number of requested random deviates.
    """
    # Draw standard deviates
    draws_standard = np.random.multivariate_normal(np.zeros(4),
        np.identity(4), (num_periods, max_draws))

    # Write to file to they can be read in by the different implementations.
    with open('draws.txt', 'w') as file_:
        for period in range(num_periods):
            for i in range(max_draws):
                fmt = ' {0:15.10f} {1:15.10f} {2:15.10f} {3:15.10f}\n'
                line = fmt.format(*draws_standard[period, i, :])
                file_.write(line)


def get_valid_values(which):
    """ Simply get a valid value.
    """
    assert which in ['amb', 'cov', 'coeff', 'delta']

    if which in ['amb', 'delta']:
        value = np.random.choice([0.0, np.random.uniform()])
    elif which in ['coeff']:
        value = np.random.uniform(-0.05, 0.05)
    elif which in ['cov']:
        value = np.random.uniform(0.05, 1)

    return value


def get_valid_bounds(which, value):
    """ Simply get a valid set of bounds.
    """
    assert which in ['amb', 'cov', 'coeff', 'delta']

    # The bounds cannot be too tight as otherwise the BOBYQA might not start
    # properly.
    if which in ['delta', 'amb']:
        upper = np.random.choice([None, value + np.random.uniform(low=0.1)])
        bounds = [max(0.0, value - np.random.uniform(low=0.1)), upper]
    elif which in ['coeff']:
        upper = np.random.choice([None, value + np.random.uniform(low=0.1)])
        lower = np.random.choice([None, value - np.random.uniform(low=0.1)])
        bounds = [lower, upper]
    elif which in ['cov']:
        bounds = [None, None]

    return bounds