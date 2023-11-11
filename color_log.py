import logging
import colorlog


def setup_logger(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.encoding = 'utf-8'

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    color_formatter = colorlog.ColoredFormatter('%(log_color)s%(levelname)s : %(message)s')

    console_handler.setFormatter(color_formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


if __name__ == '__main__':
    logger = setup_logger('log.txt')

    logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')
