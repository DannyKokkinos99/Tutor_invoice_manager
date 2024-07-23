# pylint: disable= C0116,C0114,C0115,W0612,E1133,E0401
import logging


def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if (
        not logger.handlers
    ):  # Avoid adding handlers multiple times in case of import reload
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        logger.addHandler(console_handler)

        # file_handler = logging.FileHandler("app.log")
        # file_handler.setLevel(logging.DEBUG)
        # file_handler.setFormatter(
        #     logging.Formatter(
        #         "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
        #     )
        # )
        # logger.addHandler(file_handler)

    return logger
