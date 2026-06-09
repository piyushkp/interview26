"""Port of java/Solution.java -> in-place reversal of an array-of-arrays.

Original Java package: code.ds

The reference `reverse` is an intentionally buggy in-place attempt (using only
fixed-size temporaries). It is ported faithfully, so the second printout is the
buggy result rather than a clean reverse. `reverse1` is a correct 1-D reverse.
"""

from typing import List, Optional


def print_aoa(array_of_arrays: List[List[int]]) -> None:
    print("[")
    for sub_list in array_of_arrays:
        line = "\t["
        for i in range(len(sub_list)):
            if i > 0:
                line += ", "
            line += str(sub_list[i])
        line += "]"
        print(line)
    print("]")


def reverse(aoa: List[List[int]]) -> None:
    # In-place attempt using only fixed-size temporaries (faithful, buggy).
    bottom_row = len(aoa) - 1
    bottom_col = len(aoa[bottom_row])  # noqa: F841 (kept; reassigned below like Java)
    for i in range(len(aoa)):
        bottom_row -= i
        if bottom_row == i:
            reverse1(aoa[bottom_row])
        else:
            if bottom_row >= 0:
                for j in range(len(aoa[i])):
                    bottom_col = len(aoa[bottom_row]) - 1 - j
                    if bottom_col >= 0:
                        temp = aoa[i][j]
                        aoa[i][j] = aoa[bottom_row][bottom_col]
                        aoa[bottom_row][bottom_col] = temp
                    else:
                        bottom_row -= 1  # Java: --bottomRow inside the condition
                        if bottom_row >= 0 and len(aoa[bottom_row]) - 1 >= 0:
                            bottom_col = len(aoa[bottom_row]) - 1
                            temp = aoa[i][j]
                            aoa[i][j] = aoa[bottom_row][bottom_col]
                            aoa[bottom_row][bottom_col] = temp


def reverse1(input_arr: Optional[List[int]]) -> None:
    if input_arr is None or len(input_arr) <= 1:
        return
    for i in range(len(input_arr) // 2):
        temp = input_arr[i]
        input_arr[i] = input_arr[len(input_arr) - i - 1]
        input_arr[len(input_arr) - i - 1] = temp


if __name__ == "__main__":
    array_of_arrays = [
        [],
        [1, 2, 3, 4, 5],
        [6],
        [7],
        [8, 9],
        [],
    ]
    print_aoa(array_of_arrays)
    reverse(array_of_arrays)
    print_aoa(array_of_arrays)

    reverse1([1, 2, 3, 4, 5, 6, 7])  # correct 1-D reverse (result not printed in ref)
