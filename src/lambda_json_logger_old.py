import json
import logging
import traceback


class FormatterJSON(logging.Formatter):
    def format(self, record):
        _test = record.__dict__

        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)

        log = {
            'level': record.levelname,
            'timestamp': record.asctime,
            # 'timestamp_epoch': record.created,
            # 'aws_request_id': getattr(record, 'aws_request_id', '00000000-0000-0000-0000-000000000000'),
            'message': record.getMessage(),
            # 'module': record.module,
            # 'filename': record.filename,
            # 'funcName': record.funcName,
            # 'levelno': record.levelno,
            # 'lineno': record.lineno,
            # 'traceback': {},
            # 'extra_data': record.__dict__.get('extra_data', {}),
            # 'event': record.__dict__.get('event', {}),
        }
        if record.exc_info:
            exception_data = traceback.format_exc().splitlines()
            log['traceback'] = exception_data

        return json.dumps(log, ensure_ascii=False)


logger = logging.getLogger()
logger.setLevel('INFO')

formatter = FormatterJSON(
    '[%(levelname)s]\t%(asctime)s\t%(message)s\n',
    '%Y-%m-%dT%H:%M:%SZ'
)

handler = logging.StreamHandler()
handler.setLevel('INFO')
handler.setFormatter(formatter)

# Replace the LambdaLoggerHandler formatter :
logger.addHandler(handler)


def info(message: str, code: str = '-', extra=None):
    _extra = {'code': code} | extra if extra else {'code': code}
    logger.info(message, extra=_extra)


def hello(event, context):
    try:
        # ログに表示させたい情報をdataに入れる
        value = dict(a='abc', b='def', c=123)
        # data = {"event": event}
        # data['extra_data'] = value
        # logger.info('Start hello Func', extra=value)
        info('Start hello Func', 'I0001', extra=value)

        # 例外を発生させる
        print(1 / 0)

    except ZeroDivisionError as error:
        data = {"event": event}
        logging.exception(error, extra=dict(data))


hello(event={}, context=None)
