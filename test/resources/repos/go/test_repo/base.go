package main

import "fmt"

// BaseStruct represents a base structure that can be embedded
type BaseStruct struct {
	Name string
	ID   int
}

// Execute provides a base implementation
func (b *BaseStruct) Execute() {
	fmt.Printf("Executing base with name: %s, ID: %d\n", b.Name, b.ID)
}

// GetName returns the name of the base struct
func (b *BaseStruct) GetName() string {
	return b.Name
}

// Processable interface defines processing behavior
type Processable interface {
	Process() error
	GetType() string
}

// Readable interface defines reading behavior
type Readable interface {
	Read() ([]byte, error)
}

// Writable interface defines writing behavior
type Writable interface {
	Write(data []byte) error
}

// Worker interface combines multiple behaviors
type Worker interface {
	Processable
	Execute()
}