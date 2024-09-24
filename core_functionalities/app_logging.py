import logging
import os
from logging.handlers import TimedRotatingFileHandler


def get_logger(name: str = "app_logger"):
    """
    Set up and return a logger that logs messages to both the console (stdout)
    and a rotating log file. The log file rotates daily.

    :param name: Name of the logger to create. Defaults to 'app_logger'.
    :return: Configured logger instance
    """

    # Create the logger instance with the given name
    logger = logging.getLogger(name)

    # Avoid creating multiple handlers if the logger is called multiple times
    if len(logger.handlers) > 0:
        return logger

    # Set the log level (you can adjust this as needed, DEBUG is most verbose)
    logger.setLevel(logging.DEBUG)

    # Create a directory for logs if it doesn't exist
    log_dir = os.path.join(os.path.dirname(__file__), "../logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # Log format (timestamp, file path, line number, and message)
    formatter = logging.Formatter(
        "%(asctime)s - %(pathname)s:%(lineno)d - %(levelname)s - %(message)s"
    )

    # Create file handler with daily rotation
    file_handler = TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Create console handler for stdout
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # Adjust if more verbosity is needed
    console_handler.setFormatter(formatter)

    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
