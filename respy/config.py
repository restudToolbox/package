"""General configuration for respy."""
from pathlib import Path

import numpy as np

# Obtain the root directory of the package. Do not import respy which creates a circular
# import.
ROOT_DIR = Path(__file__).parent

# Directory with additional resources for the testing harness
TEST_RESOURCES_DIR = ROOT_DIR / "tests" / "resources"

HUGE_FLOAT = 1e20
TINY_FLOAT = 1e-8
PRINT_FLOAT = 1e10

# Number of decimals that are compared for tests This is currently only used in
# regression tests.
DECIMALS = 6
# Some assert fucntions take rtol instead of decimals
TOL = 10 ** -DECIMALS

# Interpolation
INADMISSIBILITY_PENALTY = -400000

IS_DEBUG = False

BASE_COVARIATES = {
    # Experience in A or B, but not in the last period.
    "not_exp_a_lagged": "(exp_a > 0) & (choice_lagged != 1)",
    "not_exp_b_lagged": "(exp_b > 0) & (choice_lagged != 2)",
    # Last occupation was A, B, or education.
    "work_a_lagged": "choice_lagged == 1",
    "work_b_lagged": "choice_lagged == 2",
    "edu_lagged": "choice_lagged == 3",
    # No experience in A or B.
    "not_any_exp_a": "exp_a == 0",
    "not_any_exp_b": "exp_b == 0",
    # Any experience in A or B.
    "any_exp_a": "exp_a > 0",
    "any_exp_b": "exp_b > 0",
    # High school or college graduate.
    "hs_graduate": "edu >= 12",
    "co_graduate": "edu >= 16",
    # Was not in school last period and is/is not high school graduate.
    "is_return_not_high_school": "~edu_lagged & ~hs_graduate",
    "is_return_high_school": "~edu_lagged & hs_graduate",
    # Define age groups.
    "is_minor": "period < 2",
    "is_young_adult": "2 <= period <= 4",
    "is_adult": "5 <= period",
}

DEFAULT_OPTIONS = {
    "education_lagged": [1],
    "education_start": [10],
    "education_share": [1],
    "education_max": 20,
    "estimation_draws": 200,
    "estimation_seed": 1,
    "estimation_tau": 500,
    "interpolation_points": -1,
    "num_periods": 40,
    "simulation_agents": 1000,
    "simulation_seed": 2,
    "solution_draws": 500,
    "solution_seed": 3,
    "covariates": BASE_COVARIATES,
}

# Labels for columns in a dataset as well as the formatters.
DATA_LABELS_EST = [
    "Identifier",
    "Period",
    "Choice",
    "Wage",
    "Experience_A",
    "Experience_B",
    "Years_Schooling",
    "Lagged_Choice",
]

# There is additional information available in a simulated dataset.
DATA_LABELS_SIM = DATA_LABELS_EST + [
    "Type",
    "Total_Reward_1",
    "Total_Reward_2",
    "Total_Reward_3",
    "Total_Reward_4",
    "Systematic_Reward_1",
    "Systematic_Reward_2",
    "Systematic_Reward_3",
    "Systematic_Reward_4",
    "Shock_Reward_1",
    "Shock_Reward_2",
    "Shock_Reward_3",
    "Shock_Reward_4",
    "Discount_Rate",
    "Immediate_Reward_1",
    "Immediate_Reward_2",
    "Immediate_Reward_3",
    "Immediate_Reward_4",
]

DATA_FORMATS_EST = {
    col: (np.float if col == "Wage" else np.int) for col in DATA_LABELS_EST
}
DATA_FORMATS_SIM = {
    col: (np.int if col == "Type" else np.float) for col in DATA_LABELS_SIM
}
DATA_FORMATS_SIM = {**DATA_FORMATS_SIM, **DATA_FORMATS_EST}

EXAMPLE_MODELS = [
    f"kw_data_{suffix}"
    for suffix in ["one", "one_initial", "one_types", "two", "three"]
] + ["reliability_short"]
