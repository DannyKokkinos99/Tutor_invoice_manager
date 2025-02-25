# pylint: disable= C0116,C0114,C0115,W0612,E1133,E0401
import logging
import sys
import time


def init_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if (
        not logger.handlers
    ):  # Avoid adding handlers multiple times in case of import reload
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(console_handler)

    return logger


logger = init_logger(__name__)


def loading_animation(stop_signal):
    """Displays a loading animation until stop_event is set."""
    while not stop_signal.is_set():
        for dots in [".", "..", "..."]:
            sys.stdout.write(f"\rLoading{dots}   ")  # Overwrite the same line
            sys.stdout.flush()
            time.sleep(0.5)
            if stop_signal.is_set():
                break  # Exit the loop when stop event is set
    sys.stdout.write("\rDone!      \n")  # Clear loading message
