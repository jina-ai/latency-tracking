ARG JINA_VER

FROM jinaai/jina:$JINA_VER

WORKDIR workspace/

ADD app.py ./

# for comparing versions
RUN pip install packaging

# run benchmark
ENTRYPOINT ["python", "app.py"]