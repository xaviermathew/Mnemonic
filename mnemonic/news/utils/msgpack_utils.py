import datetime
import logging

import msgpack
import msgpack.exceptions

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


def streaming_loads2(stream, **kwargs):
    """
    wrapper around streaming_loads() that doesnt break on errors
    """

    input_data = streaming_loads(stream, unicode_errors='replace', **kwargs)
    while True:
        try:
            value = next(input_data)
        except ValueError:
            print('error reading entry. scanning for next good item...')
            try:
                input_data.skip()
            except msgpack.exceptions.OutOfData:
                print('error skipping data. msgpack says no more data')
                return
            while True:
                try:
                    skip_value = next(input_data)
                except StopIteration:
                    return
                else:
                    if isinstance(skip_value, dict):
                        print('found good entry')
                        yield skip_value
                        break
                    else:
                        print('skip partial entry', skip_value)
        except StopIteration:
            return
        else:
            yield value
