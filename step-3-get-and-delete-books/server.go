package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	pbBooks "github.com/mresti/grpc-workshop/step-3-get-and-delete-books/books"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

var (
	port      = flag.Int("port", 50051, "The server port")
	booksList = []*pbBooks.Book{
		{
			Id:     123,
			Title:  "A Tale of Two Cities",
			Author: "Charles Dickens",
		},
	}
)

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", fmt.Sprintf("localhost:%d", *port))
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	var opts []grpc.ServerOption
	grpcServer := grpc.NewServer(opts...)
	fmt.Println("Server running at http://0.0.0.0:50051")
	service := service{}
	pbBooks.RegisterBookServiceServer(grpcServer, &service)
	grpcServer.Serve(lis)
}

type service struct {
}

func (s *service) List(context.Context, *pbBooks.Empty) (*pbBooks.BookList, error) {
	return &pbBooks.BookList{Books: booksList}, nil
}

func (s *service) Insert(ctx context.Context, book *pbBooks.Book) (*pbBooks.Empty, error) {
	booksList = append(booksList, book)
	return &pbBooks.Empty{}, nil
}

func (s *service) Get(ctx context.Context, req *pbBooks.BookIdRequest) (*pbBooks.Book, error) {
	for i := 0; i < len(booksList); i++ {
		if booksList[i].Id == req.Id {
			return booksList[i], nil
		}
	}
	return nil, status.Errorf(codes.NotFound, "Not found")
}

func (s *service) Delete(ctx context.Context, req *pbBooks.BookIdRequest) (*pbBooks.Empty, error) {
	for i := 0; i < len(booksList); i++ {
		if booksList[i].Id == req.Id {
			booksList = append(booksList[:i], booksList[i+1:]...)
			return &pbBooks.Empty{}, nil
		}
	}
	return nil, status.Errorf(codes.NotFound, "Not found")
}
