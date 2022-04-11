import os
import time
import logging
from io import FileIO
from logging import handlers


class LogContext:
    root_path = None
    data_folder_path = None
    session_path = None
    initalized = False


LOG_FORMAT = '%(asctime)s, %(message)s'


class FileLogger:
    _logger: logging.Logger

    def __init__(self, path):
        self._logger = logging.getLogger(path)
        self._logger.propagate = False
        self._logger.setLevel(logging.INFO)

        file_output = logging.FileHandler(path, mode='w+', encoding='utf-8')
        file_output.setFormatter(logging.Formatter(LOG_FORMAT))
        self._logger.addHandler(file_output)

    def append(self, msg, *args, **kwargs):
        self._logger.info(msg, *args, **kwargs)

    def flush(self):
        pass


class RawFileLogger:
    _internal_file_access: FileIO

    def __init__(self, path, mode):
        self._internal_file_access = open(file=path, mode=mode)

    def append(self, data):
        self._internal_file_access.write(data)

    def flush(self):
        self._internal_file_access.flush()


def new_session():
    if LogContext.initalized:
        return

    root_path = os.getcwd()
    data_folder_path = os.path.join(root_path, 'data')
    if not os.path.isdir(data_folder_path):
        os.makedirs(data_folder_path)

    formatted_dir_time = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    session_path = os.path.join(
        data_folder_path, 'session_{0}'.format(formatted_dir_time))
    os.mkdir(session_path)

    LogContext.root_path = root_path
    LogContext.data_folder_path = data_folder_path
    LogContext.session_path = session_path
    LogContext.initalized = True


def create_logger(file_path) -> FileLogger:
    file_path = '{0}.log'.format(file_path)
    abs_file_path = os.path.join(LogContext.session_path, file_path)
    dir_name = os.path.dirname(abs_file_path)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    return FileLogger(abs_file_path)


def create_raw_file_logger(file_path, mode='wb') -> RawFileLogger:
    file_path = '{0}.log'.format(file_path)
    abs_file_path = os.path.join(LogContext.session_path, file_path)
    dir_name = os.path.dirname(abs_file_path)
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    return RawFileLogger(abs_file_path, mode)
