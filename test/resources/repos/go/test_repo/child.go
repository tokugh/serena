package main

import "fmt"

// ChildStruct embeds BaseStruct, inheriting its fields and methods
type ChildStruct struct {
	BaseStruct // Embedded struct - this is Go's way of inheritance
	Value      int
}

// Process implements the Processable interface
func (c *ChildStruct) Process() error {
	fmt.Printf("Processing child %s with value %d\n", c.Name, c.Value)
	return nil
}

// GetType implements the Processable interface
func (c *ChildStruct) GetType() string {
	return "ChildStruct"
}

// Execute overrides the base Execute method
func (c *ChildStruct) Execute() {
	fmt.Printf("Executing child %s with value %d\n", c.Name, c.Value)
}

// GetValue returns the child's specific value
func (c *ChildStruct) GetValue() int {
	return c.Value
}