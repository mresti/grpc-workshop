# grpc-python-workshop

In this workshop, you will learn using Python how to build a gRPC server, a gRPC client and how to deploy a gRPC server using docker.

## Steps to learn gRPC

### Get the initial files 

The source for this codelab is in `grpc-workshop/init`.

Sample project layout:  
| Name              | Description                            |  
| client.go         | Command-line client for the server API.|  
| books/books.pb.go | go library for the books gRPC service. |  

#### Step 0: Run the client application

The sample application folder contains `client.go`, a command-line client for interacting with the gRPC service that you will create in this codelab.

Now, from the project directory, run the command-line client with no arguments to view the available commands:

```commandline
$ go run client.go 
client.go is a command-line client for this codelab's gRPC service

Usage:
  client.go list                            List all books
  client.go insert <id> <title> <author>    Insert a book
  client.go get <id>                        Get a book by its ID
  client.go delete <id>                     Delete a book by its ID
  client.go watch                           Watch for inserted books
```

Try calling one of the available commands:
```commandline
$ go run client.go list
```
You will see a list of errors after a few seconds because the python gRPC server does not yet exist!
```commandline
2018/07/17 17:07:16 List books: rpc error: code = Unavailable desc = all SubConns are in TransientFailure, 
latest connection error: connection error: desc = "transport: Error while dialing dial tcp 0.0.0.0:50051: 
connect: connection refused"
exit status 1
```
Let's fix this!

### Step 1: List all books

In this step you will write the code to implement a Python gRPC service that lists books.

gRPC services are defined in `.proto` files using the protocol buffer language.

The [Protocol Buffers Language Guide](https://developers.google.com/protocol-buffers/docs/proto3) documents the `.proto` file format.

The protocol buffer language is used to define services and message types.

Let's start by defining a service for books!

In the project directory `start`, create a new file called `books.proto` and add the following:

`books.proto`
```proto
syntax = "proto3";

package books;

service BookService {
  rpc List (Empty) returns (Empty) {}
}

message Empty {}
```

This defines a new service called *BookService* using the **proto3** version of the protocol buffers language. This is the latest version of protocol buffers and is recommended for use with gRPC.

From this proto file we will generate Go file that wraps the gRPC connection for us.
The generated files contain structs from all the "messages" defined in the proto files, and getters and setters to all structs.
Also, generated files contain gRPC client and server wrappers for the service.

To generate the Python files from the proto file we need to use the following command:
  
Make sure you have protoc-gen-go in your $PATH. 
If it's not there, simply run `export PATH=$PATH:$GOPATH/bin`.

To generate the Go files from the proto file we need to use the following command:

`python -m grpc_tools.protoc -I ./books --python_out=. --grpc_python_out=. ./books/books.proto`

* `-I` indicates the path of the project the proto file is in (“.” means current directory, because we run it from the directory `start`).

* `--python_out=. --grpc_python_out=.` indicates the path of the output. “.” means current directory. This is relative to the action of the proto file. If the proto file is in books directory then the generated file will also be in the same directory if we use “.”. This regenerates `books_pb2.py` which contains our generated request and response classes and `books_pb2_grpc.py` which contains our generated client and server classes.

Now, create a file called `server.go` and this to the file:

`server.y`
```python
from concurrent import futures
import logging
import sys
import time

import grpc

# import the generated classes
import books_pb2_grpc
import books_pb2

log = logging.getLogger()
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

bookList = [books_pb2.Book(id=123, title="A Tale of Two Cities", author="Charles Dickens")]

# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    def List(self, request, context):
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("The server does not implement this method")
        return books_pb2.Empty()

# create a gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    # listen on port 50051
    logging.info('Starting server. Listening on port 50051  .')
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("server started")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt as e:
        logging.warning('Caught exception "%s"; stopping server...', e)
        server.stop(0)
        logging.warning('Server stopped; exiting.')

if __name__ == '__main__':
    serve()

```
Run `python server.py` and from another terminal tab run `go run client.go list`. The error we receive now is ``rpc error: code = Unimplemented desc = The server does not implement this method``.
This means we created a gRPC connection :) We just need to fix the List method.

Edit the files as following:

`books.proto`
```proto
syntax = "proto3";

package books;

service BookService {
  rpc List (Empty) returns (BookList) {}
}

message Empty {} 

message Book {
  int32 id = 1;
  string title = 2;
  string author = 3;
}

message BookList {
  repeated Book books = 1;
}
```

`server.py`
```python
from concurrent import futures
import logging
import sys
import time

import grpc

# import the generated classes
import books_pb2_grpc
import books_pb2

log = logging.getLogger()
log.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
log.addHandler(ch)

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

bookList = [books_pb2.Book(id=123, title="A Tale of Two Cities", author="Charles Dickens")]

# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    def List(self, request, context):
        response = books_pb2.BookList()
        response.books.extend(bookList)
        return response

# create a gRPC server
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    books_pb2_grpc.add_BookServiceServicer_to_server(BookService(), server)
    # listen on port 50051
    logging.info('Starting server. Listening on port 50051  .')
    server.add_insecure_port('[::]:50051')
    server.start()
    logging.info("server started")
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt as e:
        logging.warning('Caught exception "%s"; stopping server...', e)
        server.stop(0)
        logging.warning('Server stopped; exiting.')

if __name__ == '__main__':
    serve()
```

Run `python -m grpc_tools.protoc -I ./books --python_out=. --grpc_python_out=. ./books/books.proto`, then `python server.py` and from another terminal tab run `go run client.go list`.

You should now see this book listed!
```commandline
Server sent 1 book(s).
{
  "books": [
    {
      "id": 123,
      "title": "A Tale of Two Cities",
      "author": "Charles Dickens"
    }
  ]
}
```

### Step 2: Insert new books

In this step you will write the code to implement adding new *Book* objects via the gRPC service.

To begin, edit `books.proto` and update *BookService* to the following:

`books.proto`
```proto
service BookService {
  rpc List (Empty) returns (BookList) {}
  // add the following line
  rpc Insert (Book) returns (Empty) {}
}
```

and run `python -m grpc_tools.protoc -I ./books --python_out=. --grpc_python_out=. ./books/books.proto` 

Now add the function to `server.py` as well:

 `server.py`
```python
# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    # .... other methods

    def Insert(self, request, context):
        bookList.append(request)
        return books_pb2.Empty()
```

To test this, restart the python server and then run the go gRPC command-line client's *Insert* command, passing *id*, *title*, and *author* as arguments:
```commandline
go run client.go insert 2 "The Three Musketeers" "Alexandre Dumas"
```

You should see an empty response:
```commandline
Server response:
{}
```

To verify that the book was inserted, run the list command again to see all books:
```commandline
go run client.go list
```

You should now see 2 books listed!
```commandline
Server sent 2 book(s).
{
  "books": [
    {
      "id": 123,
      "title": "A Tale of Two Cities",
      "author": "Charles Dickens"
    },
    {
      "id": 2,
      "title": "The Three Musketeers",
      "author": "Alexandre Dumas"
    }
  ]
}
```

### Step 3: Get and delete books
In this step you will write the code to *get* and *delete* Book objects by id via the gRPC service.

#### Get a book
To begin, edit `books.proto` and update *BookService* with the following:

`books.proto`
```proto
service BookService {
  rpc List (Empty) returns (BookList) {}
  rpc Insert (Book) returns (Empty) {}
  // add the following line
  rpc Get (BookIdRequest) returns (Book) {}
}

// add the message definition below
message BookIdRequest {
  int32 id = 1;
}
```

This defines a new *Get* rpc call that takes a *BookIdRequest* as its request and returns a *Book* as its response.

A *BookIdRequest* message type is defined for requests containing only a book's id.

To implement the Get method in the server, edit `server.py` and add the following get handler function:

`server.py`
```python
# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    # .... other methods
    
    def Get(self, request, context):
        for booked in bookList:
            if booked.id ==  request.id:
                return booked

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("No book with id {} was found".format(request.id))
        return books_pb2.Book()
```

To test this, restart the node server and then run the go gRPC command-line client's get command, passing id as an argument:
```commandline
go run client.go get 123
```

You should see the book response!
```commandline
Server response:
{
  "id": 123,
  "title": "A Tale of Two Cities",
  "author": "Charles Dickens"
}
```

Now try getting a book that doesn't exist:
```commandline
go run client.go get 404
```

You should see the error message returned:
```commandline
Get book (404): rpc error: code = NotFound desc = Not found
```

#### Delete a book

Now you will write the code to *delete* a book by id.

Edit `books.proto` and add the following *Delete* rpc method:

`books.proto`
```proto
service BookService {
  // ...
  // add the delete method definition
  rpc Delete (BookIdRequest) returns (Empty) {}
}
```

Now edit `server.py` and add the following *delete* handler function:

`server.go`
```go
func (s *service) Delete (ctx context.Context, req *books.BookIdRequest) (*books.Empty, error) {
	for i := 0; i < len(bookList); i++ {
		if bookList[i].Id == req.Id {
			bookList = append(bookList[:i], bookList[i+1:]...)
			return &books.Empty{}, nil
		}
	}
	return nil, status.Errorf(codes.NotFound, "Not found")
}
```

`server.py`
```python
# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    # .... other methods

    def Delete(self, request, context):
        for booked in bookList:
            if booked.id ==  request.id:
                bookList.remove(booked)
                return books_pb2.Empty()

        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("No book with id {} was found".format(request.id))
        return books_pb2.Empty()
```

If the books array contains a *book* with the *id* requested, the book is removed, otherwise a **NOT_FOUND error** is returned.

To test this, restart the node server and then run the go gRPC command-line client to *delete* a book:
```commandline
go run client.go list
Server sent 1 book(s).
{
  "books": [
    {
      "id": 123,
      "title": "A Tale of Two Cities",
      "author": "Charles Dickens"
    }
  ]
}

go run client.go delete 123
Server response:
{}

go run client.go list
Server sent 0 book(s).
{}

go run client.go delete 123
Delete book (123): rpc error: code = 5 desc = "Not found"
```

Great!

You implemented a fully functioning gRPC service that can list, insert, get, and delete books!

### Step 4: Stream added books

In this step you will write the code to add a streaming endpoint to the service so the client can establish a stream to the server and listen for added books.
gRPC supports streaming semantics, where either the client or the server (or both) send a stream of messages on a single RPC call. The most general case is Bidirectional Streaming where a single gRPC call establishes a stream where both the client and the server can send a stream of messages to each other.

To begin, edit `books.proto` and add the following *Watch* rpc method to *BookService*:

`books.proto`
```proto
service BookService {
  // ...
  // add the watch method definition
  rpc Watch (Empty) returns (stream Book) {}
}
```

When the client calls the *Watch* method, it will establish a stream and server will be able to stream *Book* messages when books are inserted.

To implement the *Watch* method you will need to install `pyee`:
```commandline
$ pip install pyee
```

Now edit `server.py` and add the following *events* package, bookStream event listener and watch handler function:

First define the following var 

`server.py`
```python
from pyee import EventEmitter

# ...

bookStream = EventEmitter()
StreamBus = []

#...
```

and then modify the *Insert* function:
`server.py`
```python
# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    # .... other methods
    
    def Insert(self, request, context):
        bookList.append(request)
        bookStream.emit("NewBook", request)
        return books_pb2.Empty()

@bookStream.on('NewBook')
def emit_book_on_stream_bus(request):
    logging.info("Send book on StreamBus: %s" % request)
    StreamBus.append(request)
```
Handler functions for streaming rpc methods are invoked with a writable stream object.

To stream messages to the client, the stream's write() function is called when an new_book event is emitted.

Edit `server.py` and add the *Watch* function to emit when books are inserted on StreamBus:

`server.py`
```python
# create a class to define the server functions, derived from
# book_pb2_grpc.BookServiceServicer
class BookService(books_pb2_grpc.BookServiceServicer):
    # .... other methods
    
    def Watch(self, request, context):
        while 1:
            if len(StreamBus) > 0:
                for booked in StreamBus:
                    StreamBus.remove(booked)
                    yield booked
```

To test this, restart the node server and then run the go gRPC command-line client's watch command in a 3rd Cloud Shell Session:
```commandline
go run client.go watch
```
Now run the go gRPC command-line client's insert command in your main Cloud Shell session to insert a book:
```commandline
go run client.go insert 2 "The Three Musketeers" "Alexandre Dumas"
```
Check the Cloud Shell session where the client.go watch process is running. It should have printed out the inserted book!
```commandline
go run client.go watch
Server stream data received:
{
  "id": 2,
  "title": "The Three Musketeers",
  "author": "Alexandre Dumas"
}
```

Press CTRL-C to exit the client.go watch process.

### Step 5: Create gRPC client

In this step, you will write the code to implement a Python command-line client that calls your gRPC service.

The result will be functionally equivalent to the `client.go` script that you have been using so far in this codelab!

Start by running the gRPC server again if it isn't running already:
```commandline
python server.py
```

Now create a new file called `client.py` in the project directory and add the following:

`client.py`
```python
import sys

import grpc

import books_pb2 as pb
import books_pb2_grpc

def GetClient():
    # Create channel and stub to server's address and port.
    channel = grpc.insecure_channel('0.0.0.0:50051')
    stub = books_pb2_grpc.BookServiceStub(channel)
    return stub

def usage():
    print("client.py is a command-line client for this codelab's gRPC service")
    print("Usage:")
    print("\tclient.py list                            List all books")
    print("\tclient.py insert <id> <title> <author>    Insert a book")
    print("\tclient.py get <id>                        Get a book by its ID")
    print("\tclient.py delete <id>                     Delete a book by its ID")
    print("\tclient.py watch                           Watch for inserted books")

def printRespAsJson(response):
    print(response)

def doList():
    stub = GetClient()
    # Exception handling.
    try:
        # List books
        books = stub.List(pb.Empty())
        print("Server sent %s book(s).\n" % len(books.books))
        printRespAsJson(books)
    # Catch any raised errors by grpc.
    except grpc.RpcError as e:
        print('ListBooks failed with {0}: {1}'.format(e.code(), e.details()))

def main(args):
    if args[1] == "list":
        doList()
    else:
        usage()

if __name__ == '__main__':
    main(sys.argv) 
```

This requires the grpc node module and loads books.proto (exactly like you did in server.js previously).

The client object for the gRPC service is created by calling the BookService constructor, which is dynamically created from the service definition found in books.proto.

The list() function takes a request message object as a parameter ({} in this case to represent an Empty message), followed by a callback function that will be invoked with an error object (or null) and a response message object (a Book message in this case).

`books.proto`
```proto
service BookService {
  rpc List (Empty) returns (BookList) {}
  rpc Insert (Book) returns (Empty) {}
  rpc Get (BookIdRequest) returns (Book) {}
  rpc Delete (BookIdRequest) returns (Empty) {}
  rpc Watch (Empty) returns (stream Book) {}
}
```

This means that you can now *list()*, *insert()*, *get()*, *delete()*, and *watch()* books!

Now run the command-line client:

```commandline
python client.py list
{ books: 
   [ { id: 123,
       title: 'A Tale of Two Cities',
       author: 'Charles Dickens' } ] }
```

You should see books listed!

Next, to implement the command-line client, update client.py with functions for *list()*, *insert()*, *get()* and *delete()*:

`client.py`
```python
# ...

def doList():
    stub = GetClient()
    # Exception handling.
    try:
        # List books
        books = stub.List(pb.Empty())
        print("Server sent %s book(s).\n" % len(books.books))
        printRespAsJson(books)
    # Catch any raised errors by grpc.
    except grpc.RpcError as e:
        print('ListBooks failed with {0}: {1}'.format(e.code(), e.details()))

def doGet(bookId):
    stub = GetClient()
    # Exception handling.
    try:
        # Get book
        response = stub.Get(pb.BookIdRequest(id=int(bookId)))
        print("Server response:")
        printRespAsJson(response)
    # Catch any raised errors by grpc.
    except grpc.RpcError as e:
        print('GetBook failed with {0}: {1}'.format(e.code(), e.details()))

def doInsert(bookId,bookTitle,bookAuthor):
    stub = GetClient()
    # Exception handling.
    try:
        # Insert book
        response = stub.Insert(pb.Book(id=int(bookId), title=bookTitle, author=bookAuthor))
        print("Server response:")
        printRespAsJson(response)
    # Catch any raised errors by grpc.
    except grpc.RpcError as e:
        print('InsertBook failed with {0}: {1}'.format(e.code(), e.details()))

def doDelete(bookId):
    stub = GetClient()
    # Exception handling.
    try:
        # Insert book
        response = stub.Delete(pb.BookIdRequest(id=int(bookId)))
        print("Server response:")
        printRespAsJson(response)
    # Catch any raised errors by grpc.
    except grpc.RpcError as e:
        print('DeleteBook failed with {0}: {1}'.format(e.code(), e.details()))

def main(args):
    if args[1] == "list":
        doList()
    elif args[1] == "insert":
        doInsert(args[2],args[3],args[4])
    elif args[1] == "get":
        doGet(args[2])
    elif args[1] == "delete":
        doDelete(args[2])
    else:
        usage()

if __name__ == '__main__':
    main(sys.argv)
```

To implement the *watch()* function, which receives a stream of Book messages, an event handler is registered:

`client.py`
```python
# ...

def doWatch():
    stub = GetClient()
    print("Server stream data received:")
    stream = stub.Watch(pb.Empty())
    try:
        for book in stream:
            printRespAsJson(book)
    except grpc._channel._Rendezvous as err:
        print(err)

def main(args):
    if args[1] == "list":
        doList()
    elif args[1] == "insert":
        doInsert(args[2],args[3],args[4])
    elif args[1] == "get":
        doGet(args[2])
    elif args[1] == "delete":
        doDelete(args[2])
    elif args[1] == "watch":
        doWatch()
    else:
        usage()

# ...
```

The *doWatch* function will be called with a Book message object whenever a book is inserted.

All of the commands you previously ran via client.go should now be available via your Node.js gRPC command-line client!

```commandline
$ python client.py insert 2 "The Three Musketeers" "Alexandre Dumas"
{}

$ python client.py list
{ books: 
   [ { id: 123,
       title: 'A Tale of Two Cities',
       author: 'Charles Dickens' },
     { id: 2,
       title: 'The Three Musketeers',
       author: 'Alexandre Dumas' } ] }

$ python client.py delete 123
{}

$ python client.py list
{ books: 
   [ { id: 2,
       title: 'The Three Musketeers',
       author: 'Alexandre Dumas' } ] }

$ python client.py get 2
{ id: 2,
  title: 'The Three Musketeers',
  author: 'Alexandre Dumas' }
```

In this step, you wrote a command-line client in Python that interacts with your gRPC service.

### Step 6: Deploy a gRPC server on docker-compose (optional)

In this step, we deploy the python gRPC server on docker-compose, but we need to change the address and port to listen the gRPC server.

We listen the request for the gRPC server any address when we try to run a gRPC server over docker infrastructure.

Next step, is create a dockerfile with docker, we use docker image for python version 3.7 `python:3.7`. 

So that we create a file `Dockerfile`

```dockerfile
FROM python:3.7
ADD . /code
WORKDIR /code
# install python dependencies
RUN pip install -r requirements.txt

# Run api server
CMD python server.py
```

Now, we have our docker with our gRPC server. 

Next step, we create a docker-compose file where we run our docker image. So that we create a file `docker-compose.yml`

```yml
version: '3'
services:
  server:
    build:
      context: .
      dockerfile: ./Dockerfile
    logging:
      driver: json-file
    ports:
      - "50051:50051"
```

Now, we build the images using below command:

```commandline
docker-compose build
```

Let's go to up the infrastructure using command:

```commandline
docker-compose up
```

At the end, we test using our infrastructure using our clients.

Test using golang client:

```commandline
go run client.go list
```
```commandline
go run client.go get 123
```
```commandline
go run client.go list
```
```commandline
go run client.go insert 1234 "Commit Conf" "2018"
```
```commandline
go run client.go list
```

Test using python client:

```commandline
go run client.go list
```
```commandline
go run client.go get 123
```
```commandline
go run client.go list
```
```commandline
python client.py insert 1234 "Commit Conf" "2018"
```
```commandline
python client.py list
```

*Remember:* To shutdown the infrastructure using command:
```commandline
docker-compose down
```

