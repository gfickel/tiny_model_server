# Tiny Model Server

A very lightweight, simple, yet scallable Model Server.

## What does it do?

It creates a gRPC server that runs Machine Learning models, or any other code/model you may desire. It is completely framework agnostic: what you can run in Python you can serve with this Model Server. Even mixing different PyTorch, Tensorflow and ONNX models within the same server.

In order to call this server you must use the interface provided by ***model_client.py***, like the following:

```python
model = ModelClient('example', ip='localhost', port=50000)
res = model.run_image(my_image)
```

This code will pass an image to the your model *example*, defined within the ***models/*** folder. Under the hood those communications are done using Protobufs for good speed, reliability, and you may create your own Model Client in whichever language you desire.

## Why create another Model Server?

There are many reasons, some of which I've covered on my blog post (ref pending). But this is a VERY small codebase, making debuging and extending it a breeze. It is very performant, and I can put any model inside extremely easy, either using GPU, CPU, from PyTorch, ONNX, XGBoost. I've used a similar version on production for many years, with millions of calls per month on cloud, also in some On Premise solutions with real time video processing. The fact that it is this tiny and simple was never a problem, but a strength.

## How to add a model?

You must create a new folder within ***models/***, and its name should be your model identifier/name. Within this folder you must create a ***__init__.py*** that will define your model code. Look ***models/example/__init__.py*** for the example: you will need to create a class called Model, extending ModelInterface, and implement at least the method *run*.

This method will receive the data and a dict containing possible arguments, and will return its results. It is basically should contain the inference step for your model.

*get_input_shape* should return your input shape, if applicable. Otherwise it should return None.

You can also implement *run_batch* if your model benefits from batch processing, such as many GPU ML models. Otherwise, it will default to call run for each single element of the provided batch.

As a good rule of thumb, the initialization of your model should be done within your __init__ method. And thats it, you have a new model that is ready to be served :)

## How to run Tiny Model Server?

I've added a Makefile containing many options, that you can checkout running:
```sh
make help
```

One of those options is *run_docker_server* that builds a docker image and runs it on port 50000. This is the easier method, since all the requirements and environment is handled within Docker, and you just need to install it [here](https://docs.docker.com/engine/install/).

Another option is to create a local environment and run directly. You could do with the following commands:
```sh
virtualenv -p python3 .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python server.py
```

This will create a new virtual environment, install the requirements and run the server. For development practice, you may also run the tests with either:
```sh
python -m pytest -sv tests/
```
or
```sh
make run_tests
```

## 