
import json
import os
import time

from packaging import version  # not built-in, need pip install


def benchmark():
    try:
        from jina import __version__, Flow
        from jina.helloworld.fashion.helper import load_mnist
        from jina.helloworld.fashion.executors import MyEncoder, MyIndexer
        from jina.types.document.generators import from_ndarray

        from pkg_resources import resource_filename

        err_msg = ''
        index_size = 60000
        query_size = 4096
        index_time = -1
        query_time = -1
        
        os.environ['PATH'] += os.pathsep + resource_filename('jina', 'resources')
        os.environ['PATH'] += os.pathsep + resource_filename('jina', 'resources') + '/fashion/'

        for k, v in {'RESOURCE_DIR': resource_filename('jina', 'resources'),
                     'SHARDS': 4,
                     'PARALLEL': 4,
                     'REPLICAS': 4,
                     'HW_WORKDIR': 'workdir',
                     'WITH_LOGSERVER': False}.items():
            os.environ[k] = str(v)

        f = Flow().add(uses=MyEncoder).add(uses=MyIndexer)

        with f:
            # do index
            st = time.perf_counter()
            mnist_index = load_mnist('original/index')
            data_index = from_ndarray(mnist_index)
            f.index(data_index, request_size=index_size)
            index_time = time.perf_counter() - st

            # do query
            st = time.perf_counter()
            mnist_query = load_mnist('original/query')
            data_query = from_ndarray(mnist_query)
            f.search(
                data_query, 
                shuffle=True,
                request_size=query_size, 
                parameters={'top_k':50}
                )
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
        json.dump(result, fp, indent=2)


if __name__ == '__main__':
    write_stats(benchmark())
