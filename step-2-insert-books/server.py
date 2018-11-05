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

    def Insert(self, request, context):
        bookList.append(request)
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