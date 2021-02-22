import json
import os
import time

import numpy as np
from packaging import version  # not built-in, need pip install


def input_numpy(array: 'np.ndarray', axis: int = 0, size: int = None, shuffle: bool = False):
    """This function is in Jina since very early version, but it was at different places due to refactoring.
    so I copy-paste here for compatibility
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


def input_fn(fp, index=True, num_doc=None):
    """This function is used before v0.2.2"""
    from jina.helloworld.helper import load_mnist
    img_data = load_mnist(fp)
    if not index:
        # shuffle for random query
        img_data = np.take(img_data, np.random.permutation(img_data.shape[0]), axis=0)
    d_id = 0
    for r in img_data:
        yield r.tobytes()
        d_id += 1
        if num_doc is not None and d_id > num_doc:
            break


def benchmark():
    try:
        # only these three imports are immutable from 0.1 upto now
        from jina import __version__
        from jina.flow import Flow
        from jina.helloworld.helper import load_mnist

        from pkg_resources import resource_filename

        err_msg = ''
        index_size = 60000
        query_size = 4096
        index_time = -1
        query_time = -1
        
        os.environ['PATH'] += os.pathsep + resource_filename('jina', 'resources')

        for k, v in {'RESOURCE_DIR': resource_filename('jina', 'resources'),
                     'SHARDS': 4,
                     'PARALLEL': 4,
                     'REPLICAS': 4,
                     'HW_WORKDIR': 'workdir',
                     'WITH_LOGSERVER': False}.items():
            os.environ[k] = str(v)

        # do index
        f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.index.yml'))))

        st = time.perf_counter()
        with f:
            if version.Version(__version__) < version.Version('0.2.2'):
                f.index(input_fn('original/index'), batch_size=1024)
            else:
                # Flow.index_numpy is not available in the early version
                f.index(input_numpy(load_mnist('original/index')), batch_size=1024)
        index_time = time.perf_counter() - st

        # do query
        f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.query.yml'))))

        if version.Version(__version__) < version.Version('0.2.2'):
            pass
        else:
            st = time.perf_counter()
            with f:
                # Flow.search_numpy is not available in the early version
                f.search(input_numpy(load_mnist('original/query'), size=query_size), batch_size=1024, top_k=50)
            query_time = time.perf_counter() - st

    except Exception as ex:
        # either the release is broken or the API has departed
        err_msg = repr(ex)

    return {
        'version': __version__,
        'index_time': index_time,
        'query_time': query_time,
        'index_qps': index_size / index_time,
        'query_qps': query_size / query_time,
        'error': err_msg
    }


def write_stats(stats, path='output/stats.json'):
    his = []

    if os.path.exists(path):
        try:
            with open(path) as fp:
                his = json.load(fp)
        except:
            pass

    with open(path, 'w') as fp:
        his.append(stats)
        cleaned = {}

        for dd in his:
            # some versions may completely broken therefore they give unreasonably speed
            # but the truth is they are not indexing/querying accurately
            if 5000 > dd['index_qps'] > 0 and 1000 > dd['query_qps'] > 0:
                cleaned[dd['version']] = dd
            else:
                print(f'{dd} is broken')
        result = list(cleaned.values())
        result.sort(key=lambda x: version.Version(x['version']))
        json.dump(result, fp)


if __name__ == '__main__':
    write_stats(benchmark())
