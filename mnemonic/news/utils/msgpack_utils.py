import datetime
import logging

import msgpack

_LOG = logging.getLogger(__name__)


def decode_datetime(obj):
    if '__datetime__' in obj:
        try:
            if isinstance(obj['as_str'], bytes):
                obj['as_str'] = obj['as_str'].decode('utf-8')
            obj = datetime.datetime.strptime(obj['as_str'], "%Y%m%dT%H:%M:%S.%f")
        except Exception as ex:
            _LOG.warning('error decoding datetime:%s - %s', obj, ex)
            obj = None
    return obj


def encode_datetime(obj):
    if isinstance(obj, datetime.datetime):
        obj = {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f").encode()}
    return obj


def dumps(obj, **kwargs):
    return msgpack.packb(obj, default=encode_datetime, **kwargs)


def loads(packed_string, **kwargs):
    return msgpack.unpackb(packed_string, raw=False, object_hook=decode_datetime, **kwargs)


def streaming_loads(stream, **kwargs):
    return msgpack.Unpacker(stream, raw=False, object_hook=decode_datetime, **kwargs)
