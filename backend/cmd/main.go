package main

import (
	"hack/internal/pkg/server"
)

func main() {
	s := server.New(":8090")

	s.Start()
}
