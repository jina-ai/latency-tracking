#!/usr/bin/env bash

JINA_VERS=$(git ls-remote --tags https://github.com/jina-ai/jina.git "refs/tags/v*^{}" | cut -d'/' -f3 | cut -d'^' -f1 | cut -d'v' -f2 | sort -Vr | head "-$1")

DONE_VERS=$(cat /var/output/stats.json | jq ".[] |.version" -r)


for VER in $JINA_VERS
do
	if [[ $DONE_VERS =~ (^|[[:space:]])$VER($|[[:space:]]) ]]; then
      echo "$VER has been benchmarked, skip!"
    else
      docker build --build-arg JINA_VER=$VER -f latency/Dockerfile -t latency-tracking .
      docker run -v /var/output:/app/output latency-tracking
  fi
done
