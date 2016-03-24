""" This module contains some regression tests.
"""
# standard library
import numpy as np

import pytest
import os

# ROBUPY imports
from robupy import evaluate
from robupy import simulate
from robupy import process
from robupy import solve
from robupy import read

from robupy.shared.constants import TEST_RESOURCES_DIR


@pytest.mark.usefixtures('fresh_directory', 'set_seed', 'supply_resources')
class TestClass(object):
    """ This class groups together some tests.
    """
    def test_1(self):
        """ Test solution of simple model against hard-coded results.
        """

        # Solve specified economy
        robupy_obj = read(TEST_RESOURCES_DIR + '/test_first.robupy.ini')
        robupy_obj = solve(robupy_obj)
        simulate(robupy_obj)

        # Assess expected future value
        val = robupy_obj.get_attr('periods_emax')[0, :1]
        np.testing.assert_allclose(val, 103320.40501)

        # Assess evaluation
        val = evaluate(robupy_obj, process(robupy_obj))
        np.testing.assert_allclose(val, 1.97600565965)

    def test_2(self):
        """ Compare the solution of simple model against hard-coded results.
        """
        # Solve specified economy
        robupy_obj = read(TEST_RESOURCES_DIR + '/test_second.robupy.ini')
        robupy_obj = solve(robupy_obj)
        simulate(robupy_obj)

        # Distribute class attributes
        systematic = robupy_obj.get_attr('periods_payoffs_systematic')
        emax = robupy_obj.get_attr('periods_emax')

        # PERIOD 3: Check the systematic payoffs against hand calculations.
        vals = [[2.7456010000000000, 07.5383250000000000, -3999.60, 1.140]]
        vals += [[3.0343583944356758, 09.2073308658822519, -3999.60, 1.140]]
        vals += [[3.0343583944356758, 09.2073308658822519, 0000.90, 1.140]]
        vals += [[3.3534846500000000, 11.2458593100000000, 0000.40, 1.140]]
        vals += [[3.5966397255692826, 12.0612761204447200, -3999.60, 1.140]]
        vals += [[3.9749016274947495, 14.7316759204425760, -3999.60, 1.140]]
        vals += [[3.9749016274947495, 14.7316759204425760, 0000.90, 1.140]]
        vals += [[6.2338866585247175, 31.1869581683094590, -3999.60, 1.140]]
        vals += [[3.4556134647626764, 11.5883467192233920, -3999.60, 1.140]]
        vals += [[3.8190435053663370, 14.1540386453758080, -3999.60, 1.140]]
        vals += [[3.8190435053663370, 14.1540386453758080, 0000.90, 1.140]]
        vals += [[4.5267307943142532, 18.5412874597468690, -3999.60, 1.140]]
        vals += [[5.5289614776240041, 27.6603505585167470, -3999.60, 1.140]]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(systematic[2, i, :], val))

        # PERIOD 3: Check expected future values. As there are no
        # random draws, this corresponds to the maximum
        # value in the last period.
        vals = [7.53832493366, 9.20733086588, 9.20733086588, 11.2458593149]
        vals += [12.06127612040, 14.7316759204, 14.7316759204, 31.1869581683]
        vals += [11.58834671922, 14.1540386453, 14.1540386453, 18.5412874597]
        vals += [27.660350558516747]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(emax[2, i], [val]))

        # PERIOD 2: Check the systematic payoffs against hand calculations.
        vals = [[2.7456010150169163, 07.5383249336619222, -3999.60, 1.140]]
        vals += [[3.0343583944356758, 09.2073308658822519, 0000.90, 1.140]]
        vals += [[3.5966397255692826, 12.0612761204447200, -3999.60, 1.140]]
        vals += [[3.4556134647626764, 11.5883467192233920, -3999.60, 1.140]]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(systematic[1, i, :], val))

        # PERIOD 2: Check expected future values.
        vals = [18.9965372481, 23.2024229903, 41.6888863803, 29.7329464954]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(emax[1, i], [val]))

        # PERIOD 1: Check the systematic payoffs against hand calculations.
        vals = [[2.7456010150169163, 7.5383249336619222, 0.90, 1.140]]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(systematic[0, i, :], val))

        # PERIOD 1 Check expected future values.
        vals = [47.142766995]
        for i, val in enumerate(vals):
            (np.testing.assert_allclose(emax[0, 0], [val]))

        # Assess evaluation
        val  = evaluate(robupy_obj, process(robupy_obj))
        np.testing.assert_allclose(val, 0.00)

    def test_3(self):
        """ Test the solution of model with ambiguity.
        """
        # Solve specified economy
        robupy_obj = read(TEST_RESOURCES_DIR + '/test_third.robupy.ini')
        robupy_obj = solve(robupy_obj)
        simulate(robupy_obj)

        # Assess expected future value
        val = robupy_obj.get_attr('periods_emax')[0, :1]
        np.testing.assert_allclose(val, 86121.335057)

        # Assess evaluation
        val = evaluate(robupy_obj, process(robupy_obj))
        np.testing.assert_allclose(val, 1.9145852099486904)

    def test_4(self):
        """ Test the solution of model with ambiguity.
        """
        # Solve specified economy
        robupy_obj = read(TEST_RESOURCES_DIR + '/test_fourth.robupy.ini')
        robupy_obj = solve(robupy_obj)
        simulate(robupy_obj)

        # Assess expected future value
        val = robupy_obj.get_attr('periods_emax')[0, :1]
        np.testing.assert_allclose(val, 75.719528)

        # Assess evaluation
        val = evaluate(robupy_obj, process(robupy_obj))
        np.testing.assert_allclose(val, 1.9175262133973903)

    def test_5(self, versions):
        """ Test the solution of deterministic model without ambiguity,
        but with interpolation. As a deterministic model is requested,
        all versions should yield the same result without any additional effort.
        """
        # Solve specified economy
        for version in versions:

            robupy_obj = read(TEST_RESOURCES_DIR + '/test_fifth.robupy.ini')

            robupy_obj.unlock()

            robupy_obj.set_attr('version', version)

            robupy_obj.lock()

            robupy_obj = solve(robupy_obj)
            simulate(robupy_obj)

            # Assess expected future value
            val = robupy_obj.get_attr('periods_emax')[0, :1]
            np.testing.assert_allclose(val, 88750)

            # Assess evaluation
            val = evaluate(robupy_obj, process(robupy_obj))
            np.testing.assert_allclose(val, 1.0)

    def test_6(self, versions):
        """ Test the solution of deterministic model with ambiguity and
        interpolation. This test has the same result as in the absence of
        random variation in payoffs, it does not matter whether the
        environment is ambiguous or not.
        """
        # Solve specified economy
        for version in versions:

            robupy_obj = read(TEST_RESOURCES_DIR + '/test_fifth.robupy.ini')

            robupy_obj.unlock()

            robupy_obj.set_attr('version', version)

            robupy_obj.lock()

            robupy_obj = solve(robupy_obj)
            simulate(robupy_obj)

            # Assess expected future value
            val = robupy_obj.get_attr('periods_emax')[0, :1]
            np.testing.assert_allclose(val, 88750)

            # Assess evaluation
            val = evaluate(robupy_obj, process(robupy_obj))
            np.testing.assert_allclose(val, 1.0)