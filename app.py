import json
import os
import time

import numpy as np
from packaging import version


def input_numpy(array: 'np.ndarray', axis: int = 0, size: int = None, shuffle: bool = False):
    """This function is in Jina since very early version, but it was at different places due to refactoring.
    Copy-past here for compatibility
    """
    if shuffle:
        # shuffle for random query
        array = np.take(array, np.random.permutation(array.shape[0]), axis=axis)
    d = 0
    for r in array:
        yield r
        d += 1
        if size is not None and d >= size:
            break


def benchmark():
    try:
        # only these three imports are immutable from 0.1 upto now
        from jina import __version__
        from jina.flow import Flow
        from jina.helloworld.helper import load_mnist

        from pkg_resources import resource_filename

        success = True
        err_msg = ''
        index_size = 60000
        query_size = 4096
        index_time = -1
        query_time = -1

        os.environ['RESOURCE_DIR'] = resource_filename('jina', 'resources')
        os.environ['SHARDS'] = str(4)
        os.environ['PARALLEL'] = str(4)  #
        os.environ['REPLICAS'] = str(4)  # around 0.4 there was a renaming from replicas to parallel
        os.environ['HW_WORKDIR'] = 'workdir'
        os.environ['WITH_LOGSERVER'] = str(False)

        f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.index.yml'))))

        st = time.perf_counter()
        with f:
            f.index(input_numpy(load_mnist('original/index')), batch_size=1024)
        index_time = time.perf_counter() - st

        f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.query.yml'))))

        st = time.perf_counter()
        with f:
            f.search(input_numpy(load_mnist('original/query'), size=query_size), batch_size=1024, top_k=50)
        query_time = time.perf_counter() - st
    except Exception as ex:
        # either the release is broken or the API has departed
        err_msg = repr(ex)
        success = False

    return {
        'version': __version__,
        'index_time': index_time,
        'query_time': query_time,
        'index_qps': index_size / index_time,
        'query_qps': query_size / query_time,
        'error': err_msg,
        'is_success': success
    }


def write_stats(stats, path='output/stats.json'):
    his = []

    if os.path.exists(path):
        with open(path) as fp:
            his = json.load(fp)

    with open(path, 'w') as fp:
        his.append(stats)
        cleaned = []
        for dd in his:
            if 5000 > dd['index_qps'] > 0 and 1000 > dd['query_qps'] > 0:
                cleaned.append(dd)
            else:
                print(f'{dd} is broken')
        cleaned.sort(key=lambda x: version.Version(x['version']))
        json.dump(cleaned, fp)


if __name__ == '__main__':
    write_stats(benchmark())
