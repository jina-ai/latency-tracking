ARG JINA_VER

FROM jinaai/jina:$JINA_VER

WORKDIR workspace/

ADD app.py ./
ADD requirements.txt ./

# install dependencies
RUN pip install -r requirements.txt

# run benchmark
ENTRYPOINT ["python", "app.py"]