# latency-tracking

Tracking `jina` index and query speed on `jina hello-world` over the history of releases.

## Run single version

```bash
# give the version to benchmark
JINA_VER=0.7.4

# benchmark it!
docker build --build-arg JINA_VER=$JINA_VER . -t latency-tracking
docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
```

## Run all versions

Require `jq` to be installed.

```bash
bash batch.sh
```

This will run the version in reverse order, i.e. last release first.