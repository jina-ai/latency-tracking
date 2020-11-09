#!/usr/bin/env bash

JINA_VERS=$(git ls-remote --tags https://github.com/jina-ai/jina.git "refs/tags/v*^{}" | cut -d'/' -f3 | cut -d'^' -f1 | cut -d'v' -f2 | sort -Vr | head "-$1")

DONE_VERS=$(cat output/stats.json | jq ".[] |.version" -r)


for VER in $JINA_VERS
do
	if [[ $DONE_VERS =~ (^|[[:space:]])$VER($|[[:space:]]) ]]; then
      echo "$VER has been benchmarked, skip!"
    else
      docker build --build-arg JINA_VER=$VER . -t latency-tracking
      docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
  fi
done

