package main

import (
	"flag"
	"fmt"
	"log"
	"net"

	pbBooks "github.com/mresti/grpc-workshop/step-1-list-books/books"

	"golang.org/x/net/context"
	"google.golang.org/grpc"
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
