ARG JINA_VER

FROM jinaai/jina:$JINA_VER

WORKDIR /app

ADD scripts/latency-tracking .

# install dependencies
RUN pip install -r requirements.txt

# run benchmark
ENTRYPOINT ["python", "app.py"]