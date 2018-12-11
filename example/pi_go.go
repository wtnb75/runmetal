package main

import (
	"flag"
	"fmt"
	"math"
	"math/rand"
	"time"
)

func main() {
	rand.Seed(time.Now().UnixNano())
	var n int
	flag.IntVar(&n, "n", 10000000, "number of iteration")
	flag.Parse()
	c := 0

	st := time.Now().UnixNano()
	for i := 0; i < n; i++ {
		x := rand.Float32()
		y := rand.Float32()
		if math.Sqrt(float64(x*x+y*y)) < 1.0 {
			c++
		}
	}
	en := time.Now().UnixNano() - st
	fmt.Printf("pi: %d/%d*4=%f, %d nsec\n", c, n, float32(c)/float32(n)*4.0, en)
}
