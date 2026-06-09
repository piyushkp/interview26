package main

import "fmt"

func main() {
	arrayOfArrays := [][]int{
		{},
		{1, 2, 3, 4, 5},
		{6},
		{7},
		{8, 9},
		{},
	}
	printAOA(arrayOfArrays)
	reverse(arrayOfArrays)
	printAOA(arrayOfArrays)

	reverse1([]int{1, 2, 3, 4, 5, 6, 7})
}

func printAOA(arrayOfArrays [][]int) {
	fmt.Println("[")
	for _, subList := range arrayOfArrays {
		fmt.Print("\t[")
		for i := 0; i < len(subList); i++ {
			if i > 0 {
				fmt.Print(", ")
			}
			fmt.Print(subList[i])
		}
		fmt.Println("]")
	}
	fmt.Println("]")
}

// reverse reverses the array-of-arrays in place. This is a faithful port of the
// original (buggy) interview attempt: it only swaps a subset of the elements and
// is kept as-is for fidelity rather than being corrected.
func reverse(aoa [][]int) {
	bottomRow := len(aoa) - 1
	bottomCol := len(aoa[bottomRow])
	for i := 0; i < len(aoa); i++ {
		bottomRow -= i
		if bottomRow == i {
			reverse1(aoa[bottomRow])
		} else {
			if bottomRow >= 0 {
				for j := 0; j < len(aoa[i]); j++ {
					bottomCol = len(aoa[bottomRow]) - 1 - j
					if bottomCol >= 0 {
						temp := aoa[i][j]
						aoa[i][j] = aoa[bottomRow][bottomCol]
						aoa[bottomRow][bottomCol] = temp
					} else {
						bottomRow--
						if bottomRow >= 0 && len(aoa[bottomRow])-1 >= 0 {
							bottomCol = len(aoa[bottomRow]) - 1
							temp := aoa[i][j]
							aoa[i][j] = aoa[bottomRow][bottomCol]
							aoa[bottomRow][bottomCol] = temp
						}
					}
				}
			}
		}
	}
}

// reverse1 reverses a single slice in place. O(n).
func reverse1(input []int) {
	if input == nil || len(input) <= 1 {
		return
	}
	for i := 0; i < len(input)/2; i++ {
		temp := input[i]
		input[i] = input[len(input)-i-1]
		input[len(input)-i-1] = temp
	}
}
