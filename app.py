import json
import logging
import os
import shutil
import sys
import time
import timeit

import scipy.sparse as sp

# this line is needed here for measuring import time accurately for 1M imports
import_time = timeit.timeit(stmt='import jina', number=1000000)

from jina import Document, Flow, __version__
from jina.helloworld.fashion.helper import load_mnist
from jina.types.document.generators import from_ndarray
from packaging import version  # not built-in, need pip install
from pkg_resources import resource_filename

try:
    from jina.helloworld.fashion.executors import MyEncoder, MyIndexer
except:
    from jina.helloworld.fashion.my_executors import MyEncoder, MyIndexer


# declare base logger
log = logging.getLogger(__name__)


def _benchmar_import_time() -> dict[str, float]:
    """Benchmark Jina Core import time for 1M imports.

    Returns:
        A dict mapping of import time in seconds as float number.

    TODO: Figure out How we can measure the import time within a function.
    """
    return {
        'import_time': import_time
    }


def _benchmar_flows() -> dict[str, str]:
    # TODO
    fs = [
        Flow(),
        Flow().add(),
        Flow().add().add(),
        Flow().add().add(needs='gateway')]

    for f in fs:
        f.post('/', (Document() for _ in range(10000)))
        f.post('/', (Document(blob=sp.coo_matrix([0, 0, 0, 1, 0])) for _ in range(10000)))

    return {
        'flows_time': None
    }


def _benchmark_qps() -> dict[str, str]:
    """Benchmark Jina Core Indexing and Query.

    Returns:
        A dict mapping keys
    """
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

    except Exception as e:
        log.error(e)
        sys.exit(1)

    return {
        'index_time': index_time,
        'query_time': query_time,
        'index_qps': index_size / index_time,
        'query_qps': query_size / query_time,
    }


def benchmark() -> dict[str, str]:
    """Merge all benchmark results and return final stats.

    Returns:
        A dict mapping keys.
    """
    stats = {
        'version': __version__
    }
    stats.update(_benchmar_import_time())
    stats.update(_benchmark_qps())

    return stats


def write_stats(stats: dict[str, str], path: str = 'output/stats.json') -> None:
    """Write stats to a JSON file.

    Args:
        stats: This is the summary result of all benchmarks.
    """
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

    try:
        with open(path, 'w+') as fp:
            his.append(stats)
            cleaned = {}

            for dd in his:
                # some versions may completely broken therefore they give unreasonably speed
                # but the truth is they are not indexing/querying accurately
                if 5000 > dd['index_qps'] > 0 and 1000 > dd['query_qps'] > 0:
                    cleaned[dd['version']] = dd
                else:
                    log.warn(f'{dd} is broken')
            result = list(cleaned.values())
            result.sort(key=lambda x: version.Version(x['version']))
            json.dump(result, fp, indent=2)
    except Exception as e:
        log.error(e)
        sys.exit(1)


def cleanup() -> None:
    # Do the cleanup at the end of this script.
    cwd = os.getcwd()
    my_indexer_dir = os.path.join(cwd, "MyIndexer")
    if os.path.exists(my_indexer_dir):
        shutil.rmtree(my_indexer_dir)


def main() -> None:
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

    write_stats(benchmark())
    cleanup()


if __name__ == '__main__':
    main()
