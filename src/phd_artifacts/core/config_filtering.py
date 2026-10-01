from dataclasses import dataclass
from enum import StrEnum
from typing import Any

import yaml


class ConfigOperator(StrEnum):
    EQ = "="
    NE = "!="
    GT = ">"
    GE = ">="
    LT = "<"
    LE = "<="
    CONTAINS = "~="


@dataclass(frozen=True)
class ConfigFilter:
    key: str
    operator: ConfigOperator
    value: Any


_OPERATORS = (
    ConfigOperator.GE,
    ConfigOperator.LE,
    ConfigOperator.NE,
    ConfigOperator.CONTAINS,
    ConfigOperator.EQ,
    ConfigOperator.GT,
    ConfigOperator.LT,
)


def parse_config_filter(expression: str) -> ConfigFilter:
    """Parse a config filter such as 'noise.sigma=15'."""

    for operator in _OPERATORS:
        if operator.value not in expression:
            continue

        key, raw_value = expression.split(
            operator.value,
            maxsplit=1,
        )

        key = key.strip()
        raw_value = raw_value.strip()

        if not key:
            raise ValueError(f"Invalid config filter '{expression}': missing key.")

        if not raw_value:
            raise ValueError(f"Invalid config filter '{expression}': missing value.")

        value = yaml.safe_load(raw_value)

        return ConfigFilter(
            key=key,
            operator=operator,
            value=value,
        )

    raise ValueError(
        f"Invalid config filter '{expression}'. "
        "Expected formats such as key=value, key>=value or key~=value."
    )


def parse_config_filters(
    expressions: list[str],
) -> list[ConfigFilter]:
    """Parse multiple config filter expressions."""

    return [parse_config_filter(expression) for expression in expressions]


def get_config_value(
    config: dict,
    key: str,
) -> tuple[bool, Any]:
    """Resolve a dot-separated key inside a nested config."""

    value: Any = config

    for part in key.split("."):
        if not isinstance(value, dict):
            return False, None

        if part not in value:
            return False, None

        value = value[part]

    return True, value


def find_config_values(
    config: object,
    key: str,
) -> list[Any]:
    """Find all values whose key matches anywhere in a nested config."""

    values: list[Any] = []

    if isinstance(config, dict):
        for current_key, value in config.items():
            if current_key == key:
                values.append(value)

            values.extend(
                find_config_values(
                    value,
                    key,
                )
            )

    elif isinstance(config, list):
        for value in config:
            values.extend(
                find_config_values(
                    value,
                    key,
                )
            )

    return values


def matches_value(
    actual: Any,
    operator: ConfigOperator,
    expected: Any,
) -> bool:
    """Check whether one value satisfies a filter operation."""

    if operator is ConfigOperator.EQ:
        return actual == expected

    if operator is ConfigOperator.NE:
        return actual != expected

    if operator is ConfigOperator.CONTAINS:
        return str(expected).lower() in str(actual).lower()

    try:
        if operator is ConfigOperator.GT:
            return actual > expected

        if operator is ConfigOperator.GE:
            return actual >= expected

        if operator is ConfigOperator.LT:
            return actual < expected

        if operator is ConfigOperator.LE:
            return actual <= expected

    except TypeError:
        return False

    return False


def matches_config_filter(
    config: dict,
    config_filter: ConfigFilter,
) -> bool:
    """Check an exact config path against one filter."""

    found, actual = get_config_value(
        config,
        config_filter.key,
    )

    if not found:
        return False

    return matches_value(
        actual=actual,
        operator=config_filter.operator,
        expected=config_filter.value,
    )


def matches_config_filter_any(
    config: dict,
    config_filter: ConfigFilter,
) -> bool:
    """Check whether a key matches anywhere in the config."""

    values = find_config_values(
        config,
        config_filter.key,
    )

    return any(
        matches_value(
            actual=value,
            operator=config_filter.operator,
            expected=config_filter.value,
        )
        for value in values
    )


def matches_config(
    config: dict,
    filters: list[ConfigFilter],
) -> bool:
    """Check whether a config satisfies all exact-path filters."""

    return all(
        matches_config_filter(
            config,
            config_filter,
        )
        for config_filter in filters
    )


def matches_config_any(
    config: dict,
    filters: list[ConfigFilter],
) -> bool:
    """Check whether a config satisfies all any-key filters."""

    return all(
        matches_config_filter_any(
            config,
            config_filter,
        )
        for config_filter in filters
    )
