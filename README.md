# grpc-golang-workshop

In this workshop, you will learn using Golang or Python how to build a gRPC server, a gRPC client and how to deploy a gRPC server using docker.

Based on the official gRPC workshop - https://codelabs.developers.google.com/codelabs/cloud-grpc/index.html - Where I extended to include deploying gRPC server using docker and learn to implement a gRPC client/gRPC server using Golang and Python. 

## Installing the Training Material

```commandline
    $ mkdir -p $GOPATH/src/github.com/mresti && cd $_
    $ git clone https://github.com/mresti/grpc-workshop.git
```

## Go Get The Training Material

```commandline
    $ go get github.com/mresti/grpc-workshop
```

## Versions of dependencies

- gRPC version 1.16.0
- golang version 1.10.3 or above
- python version 3.6 or above

## Requirements

* Install [text editors or IDE](https://golang.org/doc/editors.html)
* Install [docker](https://www.docker.com/get-docker)
* Install [docker-compose](https://docs.docker.com/compose/install/)
* Install [Golang](https://golang.org/doc/install)
* Install [Protocol Buffers](https://github.com/google/protobuf/releases)

### Dependencies golang

* Install protoc plugin for golang:

```commandline
    $ go get -u google.golang.org/grpc
    $ go get -u github.com/golang/protobuf/proto 
    $ go get -u github.com/golang/protobuf/protoc-gen-go
``` 

### Dpendencies python

* Create a virtualenv:
```commandline
    $ pip install virtualenv
    $ virtualenv venv
    $ source venv/bin/activate   
```

* Install protoc plugin for python:

```commandline
    (venv) $ pip install grpcio
    (venv) $ pip install grpcio-tools
    (venv) $ pip install googleapis-common-protos
    (venv) $ pip install pyee
```

Or using `requirements.txt` file:
```commandline
    (venv) $ pip install -r requirements.txt
```

## Table of Contents

What we covered with this workshop:
* The Protocol Buffer Language
* How to implement a gRPC server using Go or Python
* How to implement a gRPC client using Go or Python
* How to deploy on docker a gRPC server using Go or Python language

## Steps to learn gRPC

### gRPC 101 Presentation

[Slides](https://docs.google.com/presentation/d/1dgI09a-_4dwBMLyqfwchvS6iXtbcISQPLAXL6gSYOcc/edit#slide=id.g1c2bc22a4a_0_0) that go along with the talk.

Also, see this video for general introduction to gRPC: [Talk](https://www.youtube.com/watch?v=UVsIfSfS6I4)

### Learn gRPC:

### Golang

[gRPC golang workshop](Workshop-grpc-golang.md)

### Python

[gRPC python workshop](Workshop-grpc-python.md)
