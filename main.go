package main

import "fmt"

func main() {
	// 1. Hello World
	fmt.Println("Hello, World!")

	// 2. 变量
	var major string = "区块链技术应用"
	age := 19 // 假设你19岁
	fmt.Println("我的专业是：", major, "，我今年", age, "岁")

	// 3. 循环
	// 循环 5 次，打印专升本
	for i := 1; i <= 5; i++ {
		fmt.Println("第", i, "遍：我要专升本！")
	}
}