package main

// Roman numeral conversions (decimal <-> roman).

// Implement decimal to roman and vice versa.
func romanToInt(s string) int {
	romans := map[byte]int{
		'I': 1,
		'V': 5,
		'X': 10,
		'L': 50,
		'C': 100,
		'D': 500,
		'M': 1000,
	}
	intNum := 0
	prev := 0
	for i := len(s) - 1; i >= 0; i-- {
		temp := romans[s[i]]
		if temp < prev {
			intNum -= temp
		} else {
			intNum += temp
		}
		prev = temp
	}
	return intNum
}

func IntegerToRomanNumeral(input int) string {
	if input < 1 || input > 3999 {
		return "Invalid Roman Number Value"
	}
	s := ""
	for input >= 1000 {
		s += "M"
		input -= 1000
	}
	for input >= 900 {
		s += "CM"
		input -= 900
	}
	for input >= 500 {
		s += "D"
		input -= 500
	}
	for input >= 400 {
		s += "CD"
		input -= 400
	}
	for input >= 100 {
		s += "C"
		input -= 100
	}
	for input >= 90 {
		s += "XC"
		input -= 90
	}
	for input >= 50 {
		s += "L"
		input -= 50
	}
	for input >= 40 {
		s += "XL"
		input -= 40
	}
	for input >= 10 {
		s += "X"
		input -= 10
	}
	for input >= 9 {
		s += "IX"
		input -= 9
	}
	for input >= 5 {
		s += "V"
		input -= 5
	}
	for input >= 4 {
		s += "IV"
		input -= 4
	}
	for input >= 1 {
		s += "I"
		input -= 1
	}
	return s
}
