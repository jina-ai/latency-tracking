import json
import os
import shutil
import sys
import time

from jina import Flow, __version__
from jina.helloworld.fashion.helper import load_mnist
from jina.types.document.generators import from_ndarray
from packaging import version  # not built-in, need pip install
from pkg_resources import resource_filename

try:
    from jina.helloworld.fashion.executors import MyEncoder, MyIndexer
except:
    from jina.helloworld.fashion.my_executors import MyEncoder, MyIndexer


def benchmark():
    err_msg = ''
    index_size = 60000
    query_size = 4096
    index_time = -1
    query_time = -1

    try:
        f = Flow().add(uses=MyEncoder).add(uses=MyIndexer)

        with f:
            # do index
            st = time.perf_counter()
            mnist_index = load_mnist('original/index')
            data_index = from_ndarray(mnist_index, size=index_size)
            f.index(data_index, request_size=1024)
            index_time = time.perf_counter() - st

            # do query
            st = time.perf_counter()
            mnist_query = load_mnist('original/query')
            data_query = from_ndarray(mnist_query, size=query_size)
            f.search(
                data_query,
                shuffle=True,
                request_size=1024,
                parameters={'top_k': 50}
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

    if not os.path.exists(path):
        path_dir = os.path.split(path)[0]
        if not os.path.exists(path_dir):
            os.mkdir(path_dir)

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


def cleanup():
    cwd = os.getcwd()
    my_indexer_dir = os.path.join(cwd, "MyIndexer")
    if os.path.exists(my_indexer_dir):
        shutil.rmtree(my_indexer_dir)


def main():
    os.environ['PATH'] += os.pathsep + resource_filename('jina', 'resources')
    os.environ['PATH'] += os.pathsep + \
        resource_filename('jina', 'resources') + '/fashion/'

    for k, v in {'RESOURCE_DIR': resource_filename('jina', 'resources'),
                 'SHARDS': 4,
                 'PARALLEL': 4,
                 'REPLICAS': 4,
                 'HW_WORKDIR': 'workdir',
                 'WITH_LOGSERVER': False}.items():
        os.environ[k] = str(v)

    try:
        write_stats(benchmark())
        cleanup()
    except Exception as e:
        print(e)
        cleanup()
        sys.exit(1)


if __name__ == '__main__':
    main()
