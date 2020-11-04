import json
import os
import time

from jina import __version__

success = True
err_msg = ''
index_time = -1
query_time = -1

try:
    from jina.flow import Flow
    from jina.helloworld.helper import load_mnist
    from pkg_resources import resource_filename

    os.environ['RESOURCE_DIR'] = resource_filename('jina', 'resources')
    os.environ['SHARDS'] = str(4)
    os.environ['PARALLEL'] = str(4)
    os.environ['HW_WORKDIR'] = 'workdir'
    os.environ['WITH_LOGSERVER'] = str(False)
    os.environ['OUTPUT_STATS'] = 'output/stats.json'

    f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.index.yml'))))

    st = time.perf_counter()
    with f:
        f.index_ndarray(load_mnist('original/index'), batch_size=1024)
    index_time = time.perf_counter() - st

    f = Flow.load_config(resource_filename('jina', '/'.join(('resources', 'helloworld.flow.query.yml'))))

    st = time.perf_counter()
    with f:
        f.search_ndarray(load_mnist('original/query'), batch_size=1024, top_k=50)
    query_time = time.perf_counter() - st
except Exception as ex:
    err_msg = str(ex)
    success = False

stats = {
    'version': __version__,
    'index_time': index_time,
    'query_time': query_time,
    'index_qps': 60000 / index_time,
    'query_qps': 10000 / query_time,
    'error': err_msg,
    'is_success': success
}

his = []

if os.path.exists(os.environ['OUTPUT_STATS']):
    with open(os.environ['OUTPUT_STATS']) as fp:
        his = json.load(fp)

with open(os.environ['OUTPUT_STATS'], 'w') as fp:
    his.append(stats)
    json.dump(his, fp)
