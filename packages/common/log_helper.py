import logging
import time
import os

#LOG_FORMAT = "%(relativeCreated)s - %(message)s"
LOG_FORMAT = "%(asctime)s, %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"

file_path = './data/can_{0}.log'.format(time.strftime('%Y%m%d_%H%M%S'))

folder_path = os.path.dirname(file_path)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

logging.basicConfig(filename=file_path, filemode='w+',
                    level=logging.INFO, format=LOG_FORMAT)

def log(message, *args):
    logging.info(message)
