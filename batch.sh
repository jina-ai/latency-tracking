
JINA_VERS=$(git ls-remote --tags https://github.com/jina-ai/jina.git "refs/tags/v*^{}" | cut -d'/' -f3 | cut -d'^' -f1 | cut -d'v' -f2 | sort -Vr)

for VER in $JINA_VERS
do
	docker build --build-arg JINA_VER=$VER . -t latency-tracking
  docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
done