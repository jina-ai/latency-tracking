#!/usr/bin/env bash

JINA_CODE_TAGS=($(git ls-remote --tags https://github.com/jina-ai/jina.git "refs/tags/v*^{}" | cut -d'/' -f3 | cut -d'^' -f1 | cut -d'v' -f2 | sort -Vr ))
JINA_DOCKER_TAGS=($(wget -q https://registry.hub.docker.com/v1/repositories/jinaai/jina/tags -O -  | sed -e 's/[][]//g' -e 's/"//g' -e 's/ //g' | tr '}' '\n'  | awk -F: '{print $3}'))

COMPARE_VERS=$(
  echo ${JINA_CODE_TAGS[@]} ${JINA_DOCKER_TAGS[@]} | 
  sed 's/ /\n/g' | 
  sort | 
  uniq -d | 
  sed 's/ /\n/g' | 
  sort -r | 
  head -$1
  )

DONE_VERS=$(cat output/stats.json | jq ".[] |.version" -r)

for VER in $COMPARE_VERS
do
	if [[ $DONE_VERS =~ (^|[[:space:]])$VER($|[[:space:]]) ]]; then
      echo "$VER has been benchmarked, skip!"
    else
      docker build --build-arg JINA_VER=$VER . -t latency-tracking
      docker run -v $(pwd)/output:/workspace/output -v $(pwd)/original:/workspace/original latency-tracking
  fi
done

