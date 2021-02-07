import itertools


def chunkify(iterable, chunksize):
    it = iter(iterable)
    while True:
        chunk_it = itertools.islice(it, chunksize)
        try:
            first_el = next(chunk_it)
        except StopIteration:
            return
        yield itertools.chain((first_el,), chunk_it)
