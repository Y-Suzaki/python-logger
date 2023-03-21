import json
import os
import logging
import traceback
import threading


class FormatterJSON(logging.Formatter):
    def format(self, record):
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        json_log = {
            'level': record.levelname,
            'code': record.__dict__.get('code', '-'),
            'timestamp': record.asctime,
            'message': record.getMessage()
        }

        if extra_data := record.__dict__.get('extra_data', None):
            json_log['extra_data'] = extra_data

        if trace_id := os.environ.get('_X_AMZN_TRACE_ID', None):
            json_log['trace_id'] = trace_id.split(';')[0].replace('Root=', '')

        if record.exc_info and record.exc_info[0] is not None:
            exception_data = traceback.format_exc().splitlines()
            json_log['exception'] = exception_data

        return json.dumps(json_log, ensure_ascii=False)


class LambdaJsonLogger:
    FORMATTER = FormatterJSON('[%(levelname)s]\t%(asctime)s\t%(message)s\n', '%Y-%m-%dT%H:%M:%SZ')
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_logger(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = LambdaJsonLogger(os.environ.get('LOG_LEVEL', 'DEBUG'))
        return cls._instance

    def __init__(self, level):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(level)
        self._logger.propagate = False

        if self._logger.handlers:
            for handler in self._logger.handlers:
                handler.setLevel(level)
                handler.setFormatter(self.FORMATTER)
        else:
            handler = logging.StreamHandler()
            handler.setLevel(level)
            handler.setFormatter(self.FORMATTER)
            self._logger.addHandler(handler)

    @classmethod
    def _create_extra(cls, code: str, extra_data: dict):
        _extra_data = extra_data if extra_data else {}
        return {
            'code': code,
            'extra_data': _extra_data
        }

    def debug(self, message: str, code: str = '-', extra: dict = None):
        self._logger.debug(message, extra=self._create_extra(code, extra))

    def info(self, message: str, code: str = '-', extra: dict = None):
        self._logger.info(message, extra=self._create_extra(code, extra))

    def warning(self, message: str, code: str, extra: dict = None):
        self._logger.warning(message, extra=self._create_extra(code, extra))

    def warning_with_trace(self, message: str, code: str, extra: dict = None):
        self._logger.warning(message, extra=self._create_extra(code, extra), exc_info=True)

    def error(self, message: str, code: str, extra: dict = None):
        self._logger.error(message, extra=self._create_extra(code, extra), exc_info=True)


if __name__ == '__main__':
    def raise_value_error():
        _logger = LambdaJsonLogger.get_logger()
        _logger.debug('raise_value_error.')
        raise ValueError('Invalid values.')

    _extra = {'a': 'abc', 'b': 'def', 'c': 123}

    logger = LambdaJsonLogger.get_logger()
    logger.debug('Debug logging.')
    logger.info('Info logging.\n Info logging.', extra=_extra)
    logger.info('Info logging.\n Info logging.', 'I0001', extra=_extra)
    logger.warning('Warning logging.\n Warning logging', 'W0001')
    logger.warning('Warning logging.\n Warning logging', 'W0001', extra=_extra)
    logger.error('Error logging.\n Error logging.', 'E0001')

    os.environ['_X_AMZN_TRACE_ID'] = 'Root=1-64193bc5-14fda5f13f1ccef9177e2502;Parent=a9094f386f8990fc;Sampled=1'

    try:
        raise KeyError('Error')
    except KeyError as e:
        logger.error('Error logging.', 'E0002')
        logger.warning_with_trace('Warning logging.\n Warning logging', 'W0002', _extra)

    try:
        try:
            raise_value_error()
        except ValueError as e:
            raise Exception(e)
    except Exception as e:
        logger.error(f'{str(e)=}', 'E0002', extra=_extra)
