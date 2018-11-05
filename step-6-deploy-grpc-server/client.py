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

if __name__ == '__main__':
    main(sys.argv)
