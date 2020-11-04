# latency-tracking

## Run single version

```bash
JINA_VER=0.7.4
docker build --build-arg JINA_VER=$JINA_VER . -t latency-tracking
docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
```

## Run multiple versions

