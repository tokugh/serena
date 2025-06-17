package main

import (
	"fmt"
)

// ConcreteProcessor embeds BaseStruct and implements Processable
type ConcreteProcessor struct {
	BaseStruct // Embedded struct inheritance
	data       []string
}

// Process implements the Processable interface
func (cp *ConcreteProcessor) Process() error {
	fmt.Printf("Processing data in %s: %v\n", cp.Name, cp.data)
	return nil
}

// GetType implements the Processable interface
func (cp *ConcreteProcessor) GetType() string {
	return "ConcreteProcessor"
}

// AddData adds data to the processor
func (cp *ConcreteProcessor) AddData(item string) {
	cp.data = append(cp.data, item)
}

// MultipleInterfaces implements multiple interfaces
type MultipleInterfaces struct {
	data []byte
}

// Read implements the Readable interface
func (mi *MultipleInterfaces) Read() ([]byte, error) {
	return mi.data, nil
}

// Write implements the Writable interface
func (mi *MultipleInterfaces) Write(data []byte) error {
	mi.data = data
	return nil
}

// Process implements the Processable interface
func (mi *MultipleInterfaces) Process() error {
	fmt.Printf("Processing data: %s\n", string(mi.data))
	return nil
}

// GetType implements the Processable interface
func (mi *MultipleInterfaces) GetType() string {
	return "MultipleInterfaces"
}