import pytest

from epstats.toolkit.metric import Metric, SimpleMetric
from epstats.toolkit.check import SrmCheck, SimpleSrmCheck
from epstats.toolkit.experiment import Experiment, Filter, FilterScope
from epstats.toolkit.testing import (
    evaluate_experiment_agg,
    evaluate_experiment_simple_agg,
    evaluate_experiment_by_unit,
    TestDao,
    TestData,
)


@pytest.fixture(scope="module")
def dao():
    return TestDao(TestData())


@pytest.fixture(scope="module")
def metrics():
    return [
        Metric(
            1,
            "Click-through Rate",
            "count(test_unit_type.unit.click)",
            "count(test_unit_type.global.exposure)",
        )
    ]


@pytest.fixture(scope="module")
def checks():
    return [SrmCheck(1, "SRM", "count(test_unit_type.global.exposure)")]


@pytest.fixture(scope="module")
def unit_type():
    return "test_unit_type"


def test_binary_valued(dao, metrics, checks, unit_type):
    experiment = Experiment("test-conversion", "a", metrics, checks, unit_type=unit_type)
    evaluate_experiment_agg(experiment, dao)


def test_real_valued(dao, checks, unit_type):
    experiment = Experiment(
        "test-real-valued",
        "a",
        [
            Metric(
                2,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


def test_simple_metric(dao, checks, unit_type):
    """
    This test tests SimpleMetric and SimpleSrmCheck.
    Input data are pre-aggregated in wide dataframe format.
    """
    experiment = Experiment(
        "test-simple-metric",
        "a",
        [
            SimpleMetric(1, "Click-through Rate", "clicks", "views"),
            SimpleMetric(2, "Conversion Rate", "conversions", "views"),
            SimpleMetric(3, "RPM", "bookings", "views"),
        ],
        [SimpleSrmCheck(1, "SRM", "views")],
        unit_type=unit_type,
    )
    evaluate_experiment_simple_agg(experiment, dao)


def test_unique(dao, unit_type):
    experiment = Experiment(
        "test-unique",
        "a",
        [
            Metric(
                1,
                "Unique Click-through Rate",
                "unique(test_unit_type.unit.click)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [],  # No check
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


def test_real_by_unit(dao, unit_type):
    experiment = Experiment(
        "test-real-valued",
        "a",
        [
            Metric(
                2,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.unit.exposure)",
            )
        ],
        [SrmCheck(1, "SRM", "count(test_unit_type.unit.exposure)")],
        unit_type=unit_type,
    )
    evaluate_experiment_by_unit(experiment, dao)


def test_single_metrics_in_multiple_experiment(dao, checks, unit_type):
    experiment = Experiment(
        "test-multiple",
        "a",
        [
            Metric(
                1,
                "Click-through Rate",
                "count(test_unit_type.unit.click)",
                "count(test_unit_type.global.exposure)",
            ),
            Metric(
                2,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            ),
            Metric(
                3,
                "Conversion Rate",
                "count(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            ),
        ],
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


def test_single_metric_in_multiple_experiment_1(dao, checks, unit_type):
    experiment = Experiment(
        "test-multiple",
        "a",
        [
            Metric(
                2,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


def test_single_metric_in_multiple_experiment_2(dao, metrics, checks, unit_type):
    experiment = Experiment("test-multiple", "a", metrics, checks, unit_type=unit_type)
    evaluate_experiment_agg(experiment, dao)


def test_sequential_first_day(dao, unit_type):
    """Param date_for equals to param date_from"""
    experiment = Experiment(
        "test-sequential-v1",
        "a",
        [
            Metric(
                1,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [],
        unit_type=unit_type,
        date_from="2020-01-01",
        date_to="2020-01-14",
        date_for="2020-01-01",
    )
    evaluate_experiment_agg(experiment, dao)


def test_sequential_middle(dao, unit_type):
    """Param date_for is set between params date_from and date_to"""
    experiment = Experiment(
        "test-sequential-v2",
        "a",
        [
            Metric(
                1,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [],
        unit_type=unit_type,
        date_from="2020-01-01",
        date_to="2020-01-14",
        date_for="2020-01-10",
    )
    evaluate_experiment_agg(experiment, dao)


def test_sequential_last_day(dao, unit_type):
    """Param date_for equals to param date_to"""
    experiment = Experiment(
        "test-sequential-v3",
        "a",
        [
            Metric(
                1,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [],
        unit_type=unit_type,
        date_from="2020-01-01",
        date_to="2020-01-14",
        date_for="2020-01-14",
    )
    evaluate_experiment_agg(experiment, dao)


def test_sequential_today(dao, unit_type):
    """Param date_for is not set - it is set in __init__ method to today"""
    experiment = Experiment(
        "test-sequential-v3",
        "a",
        [
            Metric(
                1,
                "Average Bookings",
                "value(test_unit_type.unit.conversion)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [],
        unit_type=unit_type,
        date_from="2020-01-01",
        date_to="2020-01-14",
    )
    evaluate_experiment_agg(experiment, dao)


def test_missing_variant(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-variant",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
        variants=["a", "b"],
    )
    evaluate_experiment_agg(experiment, dao)


def test_missing_data_unique_goal(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-data-unique-goal",
        "a",
        [
            Metric(
                1,
                "Unique Click-through Rate",
                "unique(test_unit_type.unit.click)",
                "count(test_unit_type.global.exposure)",
            )
        ],
        [SrmCheck(1, "SRM", "count(test_unit_type.global.exposure)")],
        unit_type=unit_type,
        variants=["a", "b"],
    )
    evaluate_experiment_agg(experiment, dao)


def test_dimension(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-dimension",
        "a",
        [
            Metric(
                1,
                "Views per User of Screen button-1",
                "count(test_unit_type.unit.view(element=button-1))",
                "count(test_unit_type.global.exposure)",
            ),
            Metric(
                2,
                "Views per User of Screen button-%",
                "count(test_unit_type.unit.view(element=button-%))",
                "count(test_unit_type.global.exposure)",
            ),
        ],
        [SrmCheck(1, "SRM", "count(test_unit_type.global.exposure)")],
        unit_type=unit_type,
        variants=["a", "b"],
    )
    evaluate_experiment_agg(experiment, dao)


def test_filter_scope_goal(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-dimension",
        "a",
        [
            Metric(
                1,
                "Views per User of Screen S",
                "count(test_unit_type.unit.view)",
                "count(test_unit_type.global.exposure)",
            ),
        ],
        [SrmCheck(1, "SRM", "count(test_unit_type.global.exposure)")],
        unit_type=unit_type,
        variants=["a", "b"],
        filters=[Filter("element", ["button-1"], FilterScope.goal)],
    )
    evaluate_experiment_agg(experiment, dao)


def test_degrees_of_freedom(dao, metrics, checks, unit_type):
    """Testing functions np.round() and np.trunc() used when converting degrees of freedom from float to int."""
    experiment = Experiment(
        "test-degrees-of-freedom",
        "a",
        [
            Metric(
                1,
                "Click-through Rate",
                "count(test_unit_type.unit.click)",
                "count(test_unit_type.global.exposure)",
            ),
        ],
        [SrmCheck(1, "SRM", "count(test_unit_type.global.exposure)")],
        unit_type=unit_type,
        variants=["a", "b"],
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
def test_missing_default(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-default",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
@pytest.mark.filterwarnings("ignore:divide by zero")
def test_missing_default_exposure(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-default-exposure",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
def test_missing_default_value(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-default-value",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
@pytest.mark.filterwarnings("ignore:divide by zero")
def test_missing_exposure(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-exposure",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


def test_missing_value(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-value",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
def test_bad_experiment_unit(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "bad-experiment-unit",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
def test_missing_all_value(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-all-value",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)


@pytest.mark.filterwarnings("ignore:invalid value")
def test_missing_all(dao, metrics, checks, unit_type):
    experiment = Experiment(
        "test-missing-all",
        "a",
        metrics,
        checks,
        unit_type=unit_type,
    )
    evaluate_experiment_agg(experiment, dao)
