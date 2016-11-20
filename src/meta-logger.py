from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO


class MetaLogger:
    @staticmethod
    def get_logger(name):
        if not name:
            raise ValueError('Name parameter can not be empty.')
        return MetaLogger(name)

    @staticmethod
    def __create_stream_handler(level):
        handler = StreamHandler()
        handler.setLevel(level)
        handler.setFormatter(Formatter('%(asctime)s - %(levelname)s - %(instance_id)s - %(container_id)s - %(message)s'))
        return handler

    @staticmethod
    def __get_instance_id():
        return 'i-xxxxx'

    @staticmethod
    def __get_container_id():
        return 'aabbccdd'

    def __init__(self, name):
        self.user_variables = {}
        self.user_variables['instance_id'] = MetaLogger.__get_instance_id()
        self.user_variables['container_id'] = MetaLogger.__get_container_id()
        self.logger = getLogger(name)
        self.logger.setLevel(DEBUG)
        self.logger.addHandler(MetaLogger.__create_stream_handler(DEBUG))

    def debug(self, message):
        self.logger.debug(message, extra=self.user_variables)

    def info(self, message):
        self.logger.info(message, extra=self.user_variables)

    def warn(self, message):
        self.logger.warn(message, extra=self.user_variables)

    def error(self, message):
        self.logger.error(message, extra=self.user_variables)


logger = MetaLogger('test')
logger.debug('debug test')
logger.info('info test')
logger.warn('warn test')
logger.error('error test')
