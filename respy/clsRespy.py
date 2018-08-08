import pickle as pkl
import pandas as pd
import numpy as np
import json
import copy

from respy.python.shared.shared_auxiliary import replace_missing_values
from respy.python.shared.shared_auxiliary import check_model_parameters
from respy.pre_processing.process_model import print_init_dict
from respy.python.shared.shared_auxiliary import dist_econ_paras
from respy.python.shared.shared_auxiliary import get_optim_paras
from respy.python.shared.shared_constants import PRINT_FLOAT
from respy.python.shared.shared_constants import ROOT_DIR
from respy.python.shared.shared_constants import OPT_EST_FORT
from respy.python.shared.shared_constants import OPT_EST_PYTH
from respy.pre_processing.process_model import read, convert_init_dict_to_attr_dict, \
    convert_attr_dict_to_init_dict
from respy.custom_exceptions import UserError


class RespyCls(object):
    """Class that defines a model in respy.  """

    def __init__(self, fname):
        self._set_hardcoded_attributes()
        ini = read(fname)
        self.attr = convert_init_dict_to_attr_dict(ini)
        self._update_derived_attributes()
        self._initialize_solution_attributes()

        # Status indicators
        self.attr['is_locked'] = False
        self.attr['is_solved'] = False
        self.lock()

    def _set_hardcoded_attributes(self):
        """Set attributes that can't be changed by the model specification."""
        self.derived_attributes = ['is_myopic']
        self.solution_attributes = [
            'periods_rewards_systematic', 'states_number_period',
            'mapping_state_idx', 'periods_emax', 'states_all']

    def _initialize_solution_attributes(self):
        for attribute in self.solution_attributes:
            self.attr[attribute] = None

    def update_optim_paras(self, x_econ):
        """ Update model parameters.
        """
        x_econ = copy.deepcopy(x_econ)

        self.reset()

        # Determine use of interface
        delta, coeffs_common, coeffs_a, coeffs_b, coeffs_edu, coeffs_home, \
            shocks_cov, type_shares, type_shifts = dist_econ_paras(x_econ)

        shocks_cholesky = np.linalg.cholesky(shocks_cov)

        # Distribute class attributes
        optim_paras = self.attr['optim_paras']

        # Update model parametrization
        optim_paras['shocks_cholesky'] = shocks_cholesky

        optim_paras['coeffs_common'] = coeffs_common

        optim_paras['coeffs_home'] = coeffs_home

        optim_paras['coeffs_edu'] = coeffs_edu

        optim_paras['coeffs_a'] = coeffs_a

        optim_paras['coeffs_b'] = coeffs_b

        optim_paras['delta'] = delta

        optim_paras['type_shares'] = type_shares

        optim_paras['type_shifts'] = type_shifts

        # Check integrity
        check_model_parameters(optim_paras)

        # Update class attributes
        self.attr['optim_paras'] = optim_paras

    def lock(self):
        """ Lock class instance."""
        assert (not self.attr['is_locked']), \
            'Only unlocked instances of clsRespy can be locked.'

        self._update_derived_attributes()
        self._check_integrity_attributes()
        self._check_integrity_results()
        self.attr['is_locked'] = True

    def unlock(self):
        """ Unlock class instance."""
        assert self.attr['is_locked'], \
            'Only locked instances of clsRespy can be unlocked.'

        self.attr['is_locked'] = False

    def get_attr(self, key):
        """Get attributes."""
        assert self.attr['is_locked']
        self._check_key(key)

        if key in self.solution_attributes:
            assert self.get_attr('is_solved'), 'invalid request'

        return self.attr[key]

    def set_attr(self, key, value):
        """Set attributes."""
        assert (not self.attr['is_locked'])
        self._check_key(key)

        invalid_attr = self.derived_attributes + ['optim_paras', 'init_dict']
        if key in invalid_attr:
            raise AssertionError(
                '{} must not be modified by users!'.format(key))

        if key in self.solution_attributes:
            assert not self.attr['is_solved'], \
                'Solution attributes can only be set if model is not solved.'

        self.attr[key] = value
        self._update_derived_attributes()

    def store(self, file_name):
        """Store class instance."""
        assert self.attr['is_locked']
        assert isinstance(file_name, str)
        pkl.dump(self, open(file_name, 'wb'))

    def write_out(self, fname='model.respy.ini'):
        """Write out the implied initialization file of the class instance."""
        init_dict = convert_attr_dict_to_init_dict(self.attr)
        print_init_dict(init_dict, fname)

    def reset(self):
        """ Remove solution attributes from class instance.
        """
        for label in self.solution_attributes:
            self.attr[label] = None

        self.attr['is_solved'] = False

    def check_equal_solution(self, other):
        """ Compare two class instances for equality of solution attributes."""
        assert (isinstance(other, RespyCls))

        for key_ in self.solution_attributes:
            try:
                np.testing.assert_almost_equal(
                    self.attr[key_], other.attr[key_])
            except AssertionError:
                return False

        return True

    def _update_derived_attributes(self):
        """Update derived attributes."""
        num_types = self.attr['num_types']
        self.attr['is_myopic'] = (self.attr['optim_paras']['delta'] == 0.00)[0]
        self.attr['num_paras'] = 53 + (num_types - 1) * 6

    def _check_integrity_attributes(self):
        """Check integrity of class instance.

        This testing is done the first time the class is locked and if
        the package is running in debug mode.

        """
        a = self.attr

        # We also load the full configuration.
        with open(ROOT_DIR + '/.config', 'r') as infile:
            config_dict = json.load(infile)

        # Number of parameters
        assert isinstance(a['num_paras'], int)
        assert a['num_paras'] >= 53

        # Parallelism
        assert isinstance(a['num_procs'], int)
        assert (a['num_procs'] > 0)
        if a['num_procs'] > 1:
            assert (a['version'] == 'FORTRAN')
            assert config_dict['PARALLELISM']

        # Version version of package
        assert (a['version'] in ['FORTRAN', 'PYTHON'])
        if a['version'] == 'FORTRAN':
            assert config_dict['FORTRAN']

        # Debug status
        assert (a['is_debug'] in [True, False])

        # Forward-looking agents
        assert (a['is_myopic'] in [True, False])

        # Seeds
        for seed in [a['seed_emax'], a['seed_sim'], a['seed_prob']]:
            assert (np.isfinite(seed))
            assert (isinstance(seed, int))
            assert (seed > 0)

        # Number of agents
        for num_agents in [a['num_agents_sim'], a['num_agents_est']]:
            assert (np.isfinite(num_agents))
            assert (isinstance(num_agents, int))
            assert (num_agents > 0)

        # Number of periods
        assert (np.isfinite(a['num_periods']))
        assert (isinstance(a['num_periods'], int))
        assert (a['num_periods'] > 0)

        # Number of draws for Monte Carlo integration
        assert (np.isfinite(a['num_draws_emax']))
        assert (isinstance(a['num_draws_emax'], int))
        assert (a['num_draws_emax'] >= 0)

        # Debugging mode
        assert (a['is_debug'] in [True, False])

        # Window for smoothing parameter
        assert (isinstance(a['tau'], float))
        assert (a['tau'] > 0)

        # Interpolation
        assert (a['is_interpolated'] in [True, False])
        assert (isinstance(a['num_points_interp'], int))
        assert (a['num_points_interp'] > 0)

        # Simulation of S-ML
        assert (isinstance(a['num_draws_prob'], int))
        assert (a['num_draws_prob'] > 0)

        # Maximum number of iterations
        assert (isinstance(a['maxfun'], int))
        assert (a['maxfun'] >= 0)

        # Optimizers
        assert (a['optimizer_used'] in OPT_EST_FORT + OPT_EST_PYTH)

        # Scaling
        assert (a['precond_spec']['type'] in ['identity', 'gradient', 'magnitudes'])
        for key_ in ['minimum', 'eps']:
            assert (isinstance(a['precond_spec'][key_], float))
            assert (a['precond_spec'][key_] > 0.0)

        # Education
        assert isinstance(a['edu_spec']['max'], int)
        assert a['edu_spec']['max'] > 0
        assert isinstance(a['edu_spec']['start'], list)
        assert len(a['edu_spec']['start']) == len(set(a['edu_spec']['start']))
        assert all(isinstance(item, int) for item in a['edu_spec']['start'])
        assert all(item > 0 for item in a['edu_spec']['start'])
        assert all(item <= a['edu_spec']['max'] for item in a['edu_spec']['start'])
        assert all(isinstance(item, float) for item in a['edu_spec']['share'])
        assert all(0 <= item <= 1 for item in a['edu_spec']['lagged'])
        assert all(0 <= item <= 1 for item in a['edu_spec']['share'])
        np.testing.assert_almost_equal(
            np.sum(a['edu_spec']['share']), 1.0, decimal=4)

        # Derivatives
        assert (a['derivatives'] in ['FORWARD-DIFFERENCES'])

        # Check model parameters
        check_model_parameters(a['optim_paras'])

        # Check that all parameter values are within the bounds.
        x = get_optim_paras(a['optim_paras'], a['num_paras'], 'all', True)

        # It is not clear at this point how to impose parameter constraints on
        # the covariance matrix in a flexible manner. So, either all fixed or
        # none. As a special case, we also allow for all off-diagonal elements
        # to be fixed to zero.
        shocks_coeffs = a['optim_paras']['shocks_cholesky'][np.tril_indices(4)]
        shocks_fixed = a['optim_paras']['paras_fixed'][43:53]

        all_fixed = all(is_fixed is False for is_fixed in shocks_fixed)
        all_free = all(is_free is True for is_free in shocks_fixed)

        subset_fixed = [shocks_fixed[i] for i in [1, 3, 4, 6, 7, 8]]
        subset_value = [shocks_coeffs[i] for i in [1, 3, 4, 6, 7, 8]]

        off_diagonal_fixed = all(is_free is True for is_free in subset_fixed)
        off_diagonal_value = all(value == 0.0 for value in subset_value)
        off_diagonal = off_diagonal_fixed and off_diagonal_value

        if not (all_free or all_fixed or off_diagonal):
            raise UserError(' Misspecified constraints for covariance matrix')

        # Discount rate and type shares need to be larger than on at all times.
        for label in ['paras_fixed', 'paras_bounds']:
            assert isinstance(a['optim_paras'][label], list)
            assert (len(a['optim_paras'][label]) == a['num_paras'])

        for i in range(1):
            assert a['optim_paras']['paras_bounds'][i][0] >= 0.00

        for i in range(a['num_paras']):
            lower, upper = a['optim_paras']['paras_bounds'][i]
            if lower is not None:
                assert isinstance(lower, float)
                assert lower <= x[i]
                assert abs(lower) < PRINT_FLOAT
            if upper is not None:
                assert isinstance(upper, float)
                assert upper >= x[i]
                assert abs(upper) < PRINT_FLOAT
            if (upper is not None) and (lower is not None):
                assert upper >= lower
            # At this point no bounds for the elements of the covariance matrix
            # are allowed.
            if i in range(43, 53):
                assert a['optim_paras']['paras_bounds'][i] == [None, None]

    def _check_integrity_results(self):
        """Check the integrity of the results."""
        # Check if solution attributes well maintained.
        for label in self.solution_attributes:
            if self.attr['is_solved']:
                assert (self.attr[label] is not None)
            else:
                assert (self.attr[label] is None)

        # Distribute class attributes
        num_initial = len(self.attr['edu_spec']['start'])

        # We need to carefully distinguish between the maximum level of
        # schooling individuals enter the model and the maximum level they can
        # attain.
        edu_start = self.attr['edu_spec']['start']

        edu_start_max = max(edu_start)

        edu_max = self.attr['edu_spec']['max']

        num_periods = self.attr['num_periods']

        num_types = self.attr['num_types']

        # Distribute results
        periods_rewards_systematic = self.attr['periods_rewards_systematic']

        states_number_period = self.attr['states_number_period']

        mapping_state_idx = self.attr['mapping_state_idx']

        periods_emax = self.attr['periods_emax']

        states_all = self.attr['states_all']

        # Replace missing value with NAN. This allows to easily select the
        # valid subsets of the containers
        if mapping_state_idx is not None:
            mapping_state_idx = replace_missing_values(mapping_state_idx)
        if states_all is not None:
            states_all = replace_missing_values(states_all)
        if periods_rewards_systematic is not None:
            periods_rewards_systematic = replace_missing_values(
                periods_rewards_systematic)
        if periods_emax is not None:
            periods_emax = replace_missing_values(periods_emax)

        # Check the creation of the state space
        is_applicable = (states_all is not None)
        is_applicable = is_applicable and (states_number_period is not None)
        is_applicable = is_applicable and (mapping_state_idx is not None)

        if is_applicable:
            # No values can be larger than constraint time. The exception in
            # the lagged schooling variable in the first period, which takes
            # value one but has index zero.
            for period in range(num_periods):
                assert (np.nanmax(states_all[period, :, :3]) <=
                        (period + edu_start_max))

            # Lagged schooling can only take value zero or one if finite.
            for period in range(num_periods):
                assert (np.nanmax(states_all[period, :, 3]) in [1, 2, 3, 4])
                assert (np.nanmin(states_all[period, :, :3]) == 0)

            # All finite values have to be larger or equal to zero.
            # The loop is required as np.all evaluates to FALSE for this
            # condition (see NUMPY documentation).
            for period in range(num_periods):
                assert (np.all(
                    states_all[period, :states_number_period[period]] >= 0))

            # The maximum of education years is never larger than `edu_max'.
            for period in range(num_periods):
                assert (np.nanmax(states_all[period, :, :][:, 2], axis=0) <=
                        edu_max)

            # Check for duplicate rows in each period. We only have possible
            # duplicates if there are multiple initial conditions.
            for period in range(num_periods):
                nstates = states_number_period[period]
                assert (np.sum(pd.DataFrame(
                        states_all[period, :nstates, :]).duplicated()) == 0)

            # Checking validity of state space values. All valid values need
            # to be finite.
            for period in range(num_periods):
                assert (np.all(np.isfinite(
                    states_all[period, :states_number_period[period]])))

            # There are no infinite values in final period.
            assert (np.all(np.isfinite(states_all[(num_periods - 1), :, :])))

            # Check the number of states in the first time period.
            num_states_start = num_types * num_initial * 2
            assert (np.sum(np.isfinite(
                mapping_state_idx[0, :, :, :, :])) == num_states_start)

            # Check that mapping is defined for all possible realizations of
            # the state space by period. Check that mapping is not defined for
            # all inadmissible values.
            is_infinite = np.tile(False, reps=mapping_state_idx.shape)
            for period in range(num_periods):
                # Subsetting valid indices
                nstates = states_number_period[period]
                indices = states_all[period, :nstates, :].astype('int')
                for index in indices:
                    # Check for finite value at admissible state
                    assert (np.isfinite(mapping_state_idx[period, index[0],
                            index[1], index[2], index[3] - 1, index[4]]))
                    # Record finite value
                    is_infinite[
                        period, index[0], index[1], index[2],
                        index[3] - 1, index[4]] = True
            # Check that all admissible states are finite
            assert (
                np.all(np.isfinite(mapping_state_idx[is_infinite == True])))

            # Check that all inadmissible states are infinite
            assert (np.all(np.isfinite(
                mapping_state_idx[is_infinite == False])) == False)

        # Check the calculated systematic rewards
        is_applicable = (states_all is not None)
        is_applicable = is_applicable and (states_number_period is not None)
        is_applicable = \
            is_applicable and (periods_rewards_systematic is not None)

        if is_applicable:
            # Check that the rewards are finite for all admissible values and
            # infinite for all others.
            is_infinite = np.tile(False, reps=periods_rewards_systematic.shape)
            for period in range(num_periods):
                # Loop over all possible states
                for k in range(states_number_period[period]):
                    # Check for finite value at admissible state
                    assert (np.all(np.isfinite(
                            periods_rewards_systematic[period, k, :])))
                    # Record finite value
                    is_infinite[period, k, :] = True
                # Check that all admissible states are finite
                assert (np.all(np.isfinite(
                        periods_rewards_systematic[is_infinite == True])))
                # Check that all inadmissible states are infinite
                if num_periods > 1:
                    assert (np.all(np.isfinite(
                        periods_rewards_systematic[
                            is_infinite == False])) == False)

        # Check the expected future value
        is_applicable = (periods_emax is not None)

        if is_applicable:
            # Check that the emaxs are finite for all admissible values and
            # infinite for all others.
            is_infinite = np.tile(False, reps=periods_emax.shape)
            for period in range(num_periods):
                # Loop over all possible states
                for k in range(states_number_period[period]):
                    # Check for finite value at admissible state
                    assert (np.all(np.isfinite(periods_emax[period, k])))
                    # Record finite value
                    is_infinite[period, k] = True
                # Check that all admissible states are finite
                assert (np.all(np.isfinite(periods_emax[is_infinite == True])))
                # Check that all inadmissible states are infinite
                if num_periods == 1:
                    assert (len(periods_emax[is_infinite == False]) == 0)
                else:
                    assert (np.all(np.isfinite(
                            periods_emax[is_infinite == False])) == False)

    def _check_key(self, key):
        """Check that key is present."""
        assert (key in self.attr.keys()), \
            'Invalid key requested: {}'.format(key)
