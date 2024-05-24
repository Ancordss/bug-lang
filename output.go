package main

import "fmt"

func saludar(text string) string {
	mensaje := "Hello kitty"
	fmt.Println(mensaje)
	fmt.Println(text)
	return "hola mundo"
}
func main() {
	juanito := "1234"
	fmt.Println(saludar(juanito))
	a := 112
	b := 456
	e := 4324
	t := 5435
	c := a + b + e + t
	fmt.Println(c)
	if c == 2 {
		fmt.Println("yei")
	} else {
		fmt.Println("no yei")
	}
	for i := 0; i < 21; i++ {
		fmt.Println(i)
	}
	y := 0
	for y <= 5 {
		fmt.Println("lopping")
		y += 1
	}
}
