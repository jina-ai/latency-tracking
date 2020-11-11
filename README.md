# latency-tracking

Tracking `jina` index and query speed on `jina hello-world` over the history of releases.

<img src=".github/container-env.png?raw=true" alt="Jina banner" width="50%">

## Run single version

```bash
# give the version to benchmark
JINA_VER=0.7.4

# benchmark it!
docker build --build-arg JINA_VER=$JINA_VER . -t latency-tracking
docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
```

## Run last `n` versions

Require `jq` to be installed.

```bash
bash batch.sh 5
```

This will run the last 5 versions in reverse order, i.e. last release first.