FROM python:3.11

ADD requirements.txt /code/requirements.txt
RUN python -m pip install -r /code/requirements.txt

ADD server.proto /code/server.proto
ADD models /code/models
ADD *.py /code/

RUN python -m grpc_tools.protoc -I/code/ --python_out=/code/ --pyi_out=/code/ --grpc_python_out=/code/ /code/server.proto

WORKDIR /code/
CMD python server.py