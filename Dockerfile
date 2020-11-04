ARG JINA_VER

FROM jinaai/jina:$JINA_VER

WORKDIR workspace/

ADD app.py ./

ENTRYPOINT ["python", "app.py"]