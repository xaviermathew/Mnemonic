import itertools


def get_first(iterable):
    if isinstance(iterable, list):
        return iterable[0], iterable
    else:
        first_el = next(iterable)
        return first_el, itertools.chain((first_el,), iterable)


def chunkify(iterable, chunksize):
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, chunksize)
        try:
            first_el, chunk_it = get_first(chunk_it)
        except StopIteration:
            return
        yield chunk_it
