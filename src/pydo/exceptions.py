"""Store the pydo exceptions."""


class TaskAttributeError(Exception):
    """Catch Task attribute errors."""


class DateParseError(Exception):
    """Catch date parsing errors."""


class ConfigError(Exception):
    """Catch configuration errors."""
