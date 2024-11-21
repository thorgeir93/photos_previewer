import logging


def verbose_to_log_level(verbosity: int):
    """Translate the verbosity count to logging levels.

    :param verbosity: The verbosity count.
    :return: The corresponding logging level constant.
    """
    if verbosity >= 2:
        return logging.DEBUG
    elif verbosity == 1:
        return logging.INFO
    else:
        return logging.WARNING


def setup_logging(logger_name: str, verbosity: int = 1) -> logging.Logger:
    """
    Configures logging based on verbosity level and returns a logger instance.

    :param verbosity: Verbosity level (0: WARNING, 1: INFO, 2+: DEBUG)
    :param logger_name: Name for the logger.
    :return: A logger instance.
    """
    log_level: int = verbose_to_log_level(verbosity)

    log_formatter = logging.Formatter(
        "%(asctime)s:%(name)s:%(levelname)s: %(message)s"
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)

    # Configure the root logger (or a specific logger if logger_name is provided)
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.addHandler(console_handler)

    # Avoid duplicate logs if multiple handlers are added
    logger.propagate = False

    return logger