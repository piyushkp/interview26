package main

import (
	"errors"
	"strconv"
	"strings"
)

// ---------------------------------------------------------------------------
// Expression conversion / evaluation
// ---------------------------------------------------------------------------

func isOperator(c byte) bool {
	return c == '+' || c == '-' || c == '*' || c == '/' || c == '^' ||
		c == '(' || c == ')'
}

func isSpace(c byte) bool { // Tell whether c is a space.
	return c == ' '
}

// lowerPrecedence tells whether op1 (operator on the left) has lower precedence
// than op2 (operator on the right). op1/op2 are operator characters.
func lowerPrecedence(op1, op2 byte) bool {
	switch op1 {
	case '+', '-':
		return !(op2 == '+' || op2 == '-')
	case '*', '/':
		return op2 == '^' || op2 == '('
	case '^':
		return op2 == '('
	case '(':
		return true
	default: // (shouldn't happen)
		return false
	}
}

// tokenizeExpr mimics java.util.StringTokenizer with returnDelims=true: every
// delimiter byte becomes its own token while runs of other characters form
// operand tokens.
func tokenizeExpr(s string, delims string) []string {
	var tokens []string
	var cur strings.Builder
	for i := 0; i < len(s); i++ {
		c := s[i]
		if strings.IndexByte(delims, c) >= 0 {
			if cur.Len() > 0 {
				tokens = append(tokens, cur.String())
				cur.Reset()
			}
			tokens = append(tokens, string(c))
		} else {
			cur.WriteByte(c)
		}
	}
	if cur.Len() > 0 {
		tokens = append(tokens, cur.String())
	}
	return tokens
}

// infixToPostfix returns a postfix representation of the infix expression.
func infixToPostfix(infix string) string {
	var operatorStack []string // the stack of operators
	tokens := tokenizeExpr(infix, "+-*/^() ")
	var postfix strings.Builder
	for _, token := range tokens {
		c := token[0]
		if len(token) == 1 && isOperator(c) {
			for len(operatorStack) > 0 &&
				!lowerPrecedence(operatorStack[len(operatorStack)-1][0], c) {
				// Operator on the stack does not have lower precedence, so it
				// goes before this one.
				postfix.WriteString(" ")
				postfix.WriteString(operatorStack[len(operatorStack)-1])
				operatorStack = operatorStack[:len(operatorStack)-1]
			}
			if c == ')' {
				// Output the remaining operators in the parenthesized part.
				operator := operatorStack[len(operatorStack)-1]
				operatorStack = operatorStack[:len(operatorStack)-1]
				for operator[0] != '(' {
					postfix.WriteString(" ")
					postfix.WriteString(operator)
					operator = operatorStack[len(operatorStack)-1]
					operatorStack = operatorStack[:len(operatorStack)-1]
				}
			} else {
				operatorStack = append(operatorStack, token) // push operator
			}
		} else if len(token) == 1 && isSpace(c) {
			// token was a space: ignore it
		} else {
			postfix.WriteString(" ") // output the operand
			postfix.WriteString(token)
		}
	}
	// Output the remaining operators on the stack.
	for len(operatorStack) > 0 {
		postfix.WriteString(" ")
		postfix.WriteString(operatorStack[len(operatorStack)-1])
		operatorStack = operatorStack[:len(operatorStack)-1]
	}
	return postfix.String()
}

// infixToPrefix is a placeholder describing the steps (no body in original):
// reverse, swap parentheses, convert to postfix, reverse again.
func infixToPrefix(infix string) {
}

// evaluate evaluates the specified postfix expression.
func evaluate(expr string) int {
	var stack []int
	result := 0
	for _, token := range strings.Fields(expr) {
		if isOperator(token[0]) {
			op2 := stack[len(stack)-1]
			op1 := stack[len(stack)-2]
			stack = stack[:len(stack)-2]
			result = evalSingleOp(token[0], op1, op2)
			stack = append(stack, result)
		} else {
			n, _ := strconv.Atoi(token)
			stack = append(stack, n)
		}
	}
	return result
}

func evalSingleOp(operation byte, op1, op2 int) int {
	result := 0
	switch operation {
	case '+':
		result = op1 + op2
	case '-':
		result = op1 - op2
	case '*':
		result = op1 * op2
	case '/':
		result = op1 / op2
	}
	return result
}

// rpn evaluates a reverse polish notation expression.
func rpn(ops []string) (float64, error) {
	if len(ops) == 0 {
		return 0, nil
	}
	var stack []float64
	for _, item := range ops {
		if len(stack) < 2 {
			return 0, errors.New("ps don't represent a well-formed RPN expression")
		}
		num1 := stack[len(stack)-1]
		num2 := stack[len(stack)-2]
		stack = stack[:len(stack)-2]
		switch item {
		case "+":
			stack = append(stack, num1+num2)
		case "/":
			if num1 == 0 {
				return 0, errors.New("can not divide by Zero")
			}
			stack = append(stack, num2/num1)
		case "*":
			stack = append(stack, num1*num2)
		case "-":
			stack = append(stack, num2-num1)
		default:
			num, err := strconv.ParseFloat(item, 64)
			if err != nil {
				return 0, errors.New("ps don't represent a well-formed RPN expression")
			}
			stack = append(stack, num)
		}
	}
	if len(stack) > 1 || len(stack) == 0 {
		return 0, errors.New("ps don't represent a well-formed RPN expression")
	}
	return stack[0], nil
}

// ---------------------------------------------------------------------------
// Influencer / Celebrity problems
// ---------------------------------------------------------------------------

// getInfluencer returns the index of the influencer in the following matrix or
// -1 if none exists. A person i is not an influencer if i follows any j or some
// j does not follow i.
func getInfluencer(followingMatrix [][]bool) int {
	if len(followingMatrix) == 0 || len(followingMatrix[0]) == 0 {
		return -1
	}
	// Phase 1. elimination
	c := 0 // candidate
	for i := 1; i < len(followingMatrix); i++ {
		if followingMatrix[c][i] {
			c = i // switch candidate
		}
	}
	// Phase 2. validation
	for i := 0; i < len(followingMatrix); i++ {
		if i != c && followingMatrix[c][i] {
			return -1
		}
	}
	return c
}

// findCelebrity finds a famous person who knows no one but is known by everyone.
func findCelebrity(n int) int {
	celeb := 0
	// Find an 'i' which is known by everyone but doesn't know anyone.
	for i := 1; i < n; i++ {
		if isKnow(celeb, i) {
			celeb = i
		}
	}
	// Verify the candidate.
	for i := 0; i < n; i++ {
		if i != celeb && (isKnow(celeb, i) || !isKnow(i, celeb)) {
			return -1
		}
	}
	return celeb
}

func isKnow(i, j int) bool {
	return true
}
