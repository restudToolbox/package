"""Test model generation."""
from pathlib import Path

import numpy as np
import pytest
import yaml

from respy.config import EXAMPLE_MODELS
from respy.likelihood import get_crit_func
from respy.pre_processing.model_checking import _validate_options
from respy.pre_processing.model_processing import process_params_and_options
from respy.pre_processing.model_processing import save_options
from respy.shared import get_example_model
from respy.tests.random_model import generate_random_model
from respy.tests.random_model import simulate_truncated_data


@pytest.mark.parametrize("seed", range(5))
def test_generate_random_model(seed):
    """Test if random model specifications can be simulated and processed."""
    np.random.seed(seed)

    params, options = generate_random_model()

    df = simulate_truncated_data(params, options)

    crit_func = get_crit_func(params, options, df)

    crit_val = crit_func(params)

    assert isinstance(crit_val, float)


@pytest.mark.parametrize("model_or_seed", EXAMPLE_MODELS + list(range(10)))
def test_model_options(model_or_seed):
    if isinstance(model_or_seed, str):
        _, options = get_example_model(model_or_seed)
    else:
        np.random.seed(model_or_seed)
        _, options = generate_random_model()

    _, _, options = process_params_and_options(_, options)

    _validate_options(options)


@pytest.mark.parametrize("model_or_seed", EXAMPLE_MODELS + list(range(10)))
def test_yaml_for_options(model_or_seed):
    if isinstance(model_or_seed, str):
        params, options = get_example_model(model_or_seed)
    else:
        np.random.seed(model_or_seed)
        params, options = generate_random_model()

    path = np.random.choice([Path("os.yaml"), Path("os.yml")])

    save_options(options, path)

    with open(path, "r") as y:
        options_ = yaml.safe_load(y)

    assert options == options_
