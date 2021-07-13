ARG JINA_VER

FROM jinaai/jina:$JINA_VER

WORKDIR /app

ADD scripts/latency-tracking .
ADD latency/original ./original

# install dependencies
RUN pip install -r requirements.txt

# run benchmark
ENTRYPOINT ["python", "app.py"]
