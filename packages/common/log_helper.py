import logging

LOG_FORMAT = "%(relativeCreated)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='speed.log', filemode='w+',
                    level=logging.DEBUG, format=LOG_FORMAT)


def log_speed(speed):
    logging.info(speed)
