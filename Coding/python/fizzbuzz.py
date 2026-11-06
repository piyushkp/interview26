def fizzbuzz(n=100):
    for i in range(1, n + 1):
        if i % 15 == 0:  # multiple of both 3 and 5; must be checked first
            print("fizzbuzz")
        elif i % 3 == 0:
            print("fizz")
        elif i % 5 == 0:
            print("buzz")
        else:
            print(i)


if __name__ == "__main__":
    fizzbuzz()
