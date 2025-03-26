import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

# Define project_root at module level
project_root = Path(__file__).parent.parent.parent.resolve()


def set_env_vars() -> None:
    """
    Load environment variables from configuration files.
    If ENV is not set, defaults to 'development'.
    Tries to load from .env.{ENV} first, then falls back to .env if needed.

    Raises:
        OSError: If no configuration file exists.
    """
    # Determine the project root (adjust as necessary)
    project_root = Path(__file__).parent.parent.parent.resolve()

    # Get environment, defaulting to development
    env = os.getenv("ENV", "development").lower()

    # Try environment-specific file first
    env_specific_path = project_root / f".env.{env}"
    if env_specific_path.exists():
        load_dotenv(env_specific_path)
        return

    # Fall back to default .env file
    default_env_path = project_root / ".env"
    if default_env_path.exists():
        load_dotenv(default_env_path)
        return

    # If we get here, no configuration file was found
    error_msg = "\n".join(
        [
            "No configuration file found!",
            f"Current environment: {env}",
            "Tried looking for:",
            f"  - {env_specific_path}",
            f"  - {default_env_path}",
            "\nPlease create either a .env.{ENV} file or a .env file with the required configuration.",
        ]
    )
    raise OSError(error_msg)


def validate_env_vars() -> None:
    """
    Validate that all required environment variables are set.
    """
    required_vars = ["LOG_LEVEL", "LOG_FILE_PATH"]
    if missing_vars := [var for var in required_vars if not os.getenv(var)]:
        raise OSError(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )


def configure_log_handler(
    handler: logging.Handler,
    log_level: str,
    formatter: logging.Formatter,
    logger: logging.Logger,
) -> None:
    """Configure a logging handler with the specified settings.

    Args:
        handler: The logging handler to configure
        log_level: The logging level to set
        formatter: The formatter to use for log messages
        logger: The logger to add the handler to
    """
    handler.setLevel(getattr(logging, log_level, logging.DEBUG))
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name, ensuring it's properly configured.
    If this is the first call, it will set up the root logger configuration.
    Subsequent calls will return appropriately named loggers that inherit the configuration.

    Args:
        name: The logger name, typically __name__ from the calling module

    Returns:
        logging.Logger: A configured logger instance
    """
    # Handle the case when module is run directly (__main__)
    if name == "__main__":
        # Get the caller's file path
        import inspect

        frame = inspect.stack()[1]
        module_path = Path(frame.filename)
        try:
            # Get relative path from project root to the module
            rel_path = module_path.relative_to(project_root / "src")
            # Convert path to module notation (my_app.submodule.file)
            module_name = str(rel_path.with_suffix("")).replace(os.sep, ".")
            name = module_name
        except ValueError:
            # Fallback if file is not in src directory
            name = module_path.stem

    # Get or create the logger
    logger = logging.getLogger(name)

    # If the root logger isn't configured yet, configure it
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        validate_env_vars()

        # Retrieve logging configurations from environment variables
        LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING").upper()
        LOG_FORMAT = os.getenv(
            "LOG_FORMAT",
            "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        )
        ENABLE_CONSOLE_LOGGING = os.getenv(
            "ENABLE_CONSOLE_LOGGING", "False"
        ).lower() in ["true", "1", "yes"]
        ENABLE_FILE_LOGGING = os.getenv(
            "ENABLE_FILE_LOGGING", "False"
        ).lower() in ["true", "1", "yes"]
        LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/app.log")
        LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 1048576))  # 1MB default
        LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

        # Configure the root logger
        root_logger.setLevel(getattr(logging, LOG_LEVEL, logging.DEBUG))

        # Prevent propagation beyond our root logger
        root_logger.propagate = False

        # Formatter
        formatter = logging.Formatter(LOG_FORMAT)

        # Console Handler
        if ENABLE_CONSOLE_LOGGING:
            ch = logging.StreamHandler()
            configure_log_handler(ch, LOG_LEVEL, formatter, root_logger)

        # File Handler
        if ENABLE_FILE_LOGGING:
            log_path = Path(LOG_FILE_PATH)
            if log_dir := log_path.parent:
                log_dir.mkdir(parents=True, exist_ok=True)

            fh = RotatingFileHandler(
                LOG_FILE_PATH,
                maxBytes=LOG_MAX_BYTES,
                backupCount=LOG_BACKUP_COUNT,
            )
            configure_log_handler(fh, LOG_LEVEL, formatter, root_logger)

    return logger
