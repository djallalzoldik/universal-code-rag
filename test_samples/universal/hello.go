package main

import "fmt"

type Person struct {
    Name string
    Age  int
}

func (p Person) Greet() {
    fmt.Printf("Hello, my name is %s\n", p.Name)
}

func main() {
    p := Person{Name: "Alice", Age: 30}
    p.Greet()
}
