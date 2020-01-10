"""Estimate models with the method of simulated moments (MSM).

The method of simulated moments is developed by [1], [2], and [3] and an estimation
technique where the distance between the moments of the actual data and the moments
implied by the model parameters is minimized.

References
----------
.. [1] McFadden, D. (1989). A method of simulated moments for estimation of discrete
       response models without numerical integration. Econometrica: Journal of the
       Econometric Society, 995-1026.
.. [2] Lee, B. S., & Ingram, B. F. (1991). Simulation estimation of time-series models.
       Journal of Econometrics, 47(2-3), 197-205.
.. [3] Duffie, D., & Singleton, K. (1993). Simulated Moments Estimation of Markov Models
       of Asset Prices. Econometrica, 61(4), 929-952.

"""
import copy
import functools

import numpy as np
import pandas as pd

from respy.simulate import get_simulate_func


def get_msm_func(
    params,
    options,
    calc_moments,
    replace_nans,
    empirical_moments,
    weighting_matrix,
    return_scalar,
):
    """Get the msm function.

    Parameters
    ----------
    params : pandas.DataFrame or pandas.Series
        Contains parameters.
    options : dict
        Dictionary containing model options.
    calc_moments: callable or list
        Function(s) used to calculate simulated moments. Must match structure
        of empirical moments i.e. if empirical_moments is a list of
        pandas.DataFrames, calc_moments must be a list of the same length
        containing functions that correspond to the moments in
        empirical_moments.
    replace_nans: callable or list
        Functions(s) specifying how to handle missings in simulated_moments.
        Must match structure of empirical_moments.
        Exception: If only one replacement function is specified, it will be
        used on all sets of simulated moments.
    empirical_moments: pandas.DataFrame or pandas.Series or dict or list
        Contains the empirical moments calculated for the observed data. Moments
        should be saved to pandas.DataFrame or pandas.Series that can either be
        passed to the function directly or as items of a list or dictionary.
    weighting_matrix: numpy.ndarray
        Square matrix of dimension (NxN) with N denoting the number of
        empirical_moments. Used to weight squared moment errors.
    return_scalar: bool
        Indicates whether to return moment error vector (False) or weighted
        square product of moment error vector (True).

    Returns
    -------
    msm_func: callable
        MSM function where all arguments except the parameter vector are set.

    """
    empirical_moments = copy.deepcopy(empirical_moments)

    simulate = get_simulate_func(params, options)

    empirical_moments = _harmonize_input(empirical_moments)
    calc_moments = _harmonize_input(calc_moments)
    replace_nans = _harmonize_input(replace_nans)

    # If only one replacement function is given for multiple sets of moments, duplicate
    # replacement function for all sets of simulated moments.
    if len(replace_nans) == 1 and len(empirical_moments) > 1:
        replace_nans = replace_nans * len(empirical_moments)

    elif 1 < len(replace_nans) < len(empirical_moments):
        raise ValueError(
            "Replacement functions can only be matched 1:1 or 1:n with sets of "
            "empirical moments."
        )

    elif len(replace_nans) > len(empirical_moments):
        raise ValueError(
            "There are more replacement functions than sets of empirical moments."
        )

    else:
        pass

    # Raise error of calc_moments and empirical_moments do not match.
    if len(calc_moments) != len(empirical_moments):
        raise ValueError(
            "Number of functions to calculate simulated moments must be equal to "
            "the number of sets of empirical moments."
        )

    msm_func = functools.partial(
        msm,
        simulate=simulate,
        calc_moments=calc_moments,
        replace_nans=replace_nans,
        empirical_moments=empirical_moments,
        weighting_matrix=weighting_matrix,
        return_scalar=return_scalar,
    )

    return msm_func


def msm(
    params,
    simulate,
    calc_moments,
    replace_nans,
    empirical_moments,
    weighting_matrix,
    return_scalar,
):
    """Loss function for msm estimation.

    Parameters
    ----------
    params : pandas.DataFrame or pandas.Series
        Contains model parameters.
    simulate : callable
        Function used to simulate data for msm estimation.
    calc_moments : list
        List of function(s) used to calculate simulated moments. Must match length of
        empirical_moments i.e. calc_moments contains a moments function for each item in
        empirical_moments.
    replace_nans : list
        List of functions(s) specifying how to handle missings in simulated_moments.
        Must match length of empirical_moments.
    empirical_moments : list
        Contains the empirical moments calculated for the observed data. Each item in
        the list constitutes a set of moments saved to a pandas.DataFrame or
        pandas.Series.
    weighting_matrix : numpy.ndarray
        Square matrix of dimension (NxN) with N denoting the number of
        empirical_moments. Used to weight squared moment errors.
    return_scalar : bool
        Indicates whether to return moment error vector (False) or weighted square
        product of moment error vector (True).

    Returns
    -------
    out : pandas.Series or float
        Scalar or moment error vector depending on value of return_scalar.

    """
    empirical_moments = copy.deepcopy(empirical_moments)

    df = simulate(params)
    simulated_moments = [func(df) for func in calc_moments]

    simulated_moments = _reindex_simulated_moments(empirical_moments, simulated_moments)

    simulated_moments = [func(mom) for mom, func in zip(simulated_moments, replace_nans)]

    flat_empirical_moments = _flatten_index(empirical_moments)
    flat_simulated_moments = _flatten_index(simulated_moments)

    moment_errors = flat_empirical_moments - flat_simulated_moments

    # Return moment errors as indexed DataFrame or calculate weighted square product of
    # moment errors depending on return_scalar.
    if return_scalar is False:
        out = moment_errors
    else:
        out = moment_errors.T @ weighting_matrix @ moment_errors

    return out


def get_diag_weighting_matrix(empirical_moments, weights=None):
    """Create a diagonal weighting matrix from weights.

    Parameters
    ----------
    empirical_moments : pandas.DataFrame or pandas.Series or dict or list
        Contains the empirical moments calculated for the observed data. Moments should
        be saved to pandas.DataFrame or pandas.Series that can either be passed to the
        function directly or as items of a list or dictionary.
    weights : pandas.DataFrame or pandas.Series or dict or list
        Contains weights (usually variances) of empirical moments. Must match structure
        of empirical_moments i.e. if empirical_moments is a list of pandas.DataFrames,
        weights be list of pandas.DataFrames as well where each DataFrame entry contains
        the weight for the corresponding moment in empirical_moments.

    Returns
    -------
    numpy.ndarray
        Array contains a diagonal weighting matrix.

    """
    weights = copy.deepcopy(weights)
    empirical_moments = copy.deepcopy(empirical_moments)
    empirical_moments = _harmonize_input(empirical_moments)

    # Use identity matrix if no weights are specified.
    if weights is None:
        weights = copy.deepcopy(empirical_moments)
        for df in weights:
            df[:] = 1

    # Harmonize input weights.
    else:
        weights = _harmonize_input(weights)

    # Reindex weights to ensure they are assigned to the correct moments in the
    # msm function.
    weights = _reindex_simulated_moments(empirical_moments, weights)

    flat_weights = _flatten_index(weights)

    return np.diag(flat_weights) #np.diag(flat_weights.iloc[:, 0])


def get_flat_moments(empirical_moments):
    """Compute the empirical moments flat indexes.

    Parameters
    ----------
    empirical_moments : pandas.DataFrame or pandas.Series or dict or list
        containing pandas.DataFrame or pandas.Series. Contains the empirical moments
        calculated for the observed data. Moments should be saved to pandas.DataFrame or
        pandas.Series that can either be passed to the function directly or as items of
        a list or dictionary.

    Returns
    -------
    flat_empirical_moments : pandas.DataFrame
        Vector of empirical_moments with flat index.

    """
    empirical_moments = copy.deepcopy(empirical_moments)
    empirical_moments = _harmonize_input(empirical_moments)
    flat_empirical_moments = _flatten_index(empirical_moments)

    return flat_empirical_moments


def _harmonize_input(data):
    """Harmonize different types of inputs by turning all inputs into lists.

    - pandas.DataFrames/Series and callable functions will turn into a list containing a
      single item (i.e. the input).
    - Dictionaries will be sorted according to keys and then turn into a list containing
      the dictionary entries.

    """
    # Convert single DataFrames, Series or function into list containing one item.
    if isinstance(data, (pd.DataFrame, pd.Series)) or callable(data):
        data = [data]

    # Sort dictionary according to keys and turn into list.
    elif isinstance(data, dict):
        data = [data[key] for key in sorted(data)]

    elif isinstance(data, list):
        pass

    else:
        raise TypeError(
            "Function only accepts lists, dictionaries, functions, Series and "
            "DataFrames as inputs."
        )

    return data


def _reindex_simulated_moments(empirical_moments, simulated_moments):
    """Reindex data in simulated_moments to match index of empirical_moments."""
    simulated_moments_reindexed = []

    for emp_mom, sim_mom in zip(empirical_moments, simulated_moments):
        if isinstance(emp_mom, pd.DataFrame):
            sim_mom = sim_mom.reindex(index=emp_mom.index, columns=emp_mom.columns)
        elif isinstance(emp_mom, pd.Series):
            sim_mom = sim_mom.reindex(index=emp_mom.index)
        else:
            raise ValueError("Empirical and simulated moments must be saved to "
                             "pd.Series or pd.DataFrame.")

        simulated_moments_reindexed.append(sim_mom)

    return simulated_moments_reindexed


def _flatten_index(data):
    """Flatten the index as a combination of the former index and the columns."""
    data_flat = []
    for df in data:
        # Unstack df to add columns to index and flatten indexes for the new df.
        df.index = df.index.map(str)
        if isinstance(df,pd.DataFrame):
            df = df.unstack()
        else:
            pass

        index_flat = df.index.to_flat_index().str.join("_")
        # Drop old and add new index to data.
        df.index = index_flat

        # Add df to list.
        data_flat.append(df)

    return pd.concat(data_flat)
