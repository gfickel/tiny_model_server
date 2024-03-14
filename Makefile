# Use a single shell
.ONESHELL:

# So we can use $$(variable) on the prerequisites, that expand at matching time
.SECONDEXPANSION:

# shell settings
SHELL       := /bin/bash
.SHELLFLAGS := -e -u -c

.PHONY: build run_server run_client

## Print Makefile documentation
help:
	@perl -0 -nle 'printf("%-25s - %s\n", "$$2", "$$1") while m/^##\s*([^\r\n]+)\n^([\w-]+):[^=]/gm' \
		$(MAKEFILE_LIST) | sort
	printf "\n"
	perl -0 -nle 'printf("%-25s - %s\n", "$$2=", "$$1") while m/^##\s*([^\r\n]+)\n^([\w-]+)\s*:=/gm' \
		$(MAKEFILE_LIST) | sort


## builds the protobuf related stuff
build_server:
	python -m grpc_tools.protoc -I. --python_out=./ --pyi_out=./ --grpc_python_out=./ server.proto

## run the server
run_server: build_server
	python server.py

## run the client
run_tests: build
	python -m pytest tests/

## removes server container
remove_container:
	sudo docker rm -f model_server

## builds docker image
build_docker: remove_container
	sudo DOCKER_BUILDKIT=1 docker build --squash -t tiny_model_server/server:latest -f Dockerfile .

## builds and runs the docker image for tiny model server
run_docker_server: build_docker
	sudo docker run -d -p 50000:50000 --rm --name model_server tiny_model_server/server:latest && sudo docker logs -f model_server
	

clean:
	find . -name __pycache__ | xargs sudo rm -rvf 
