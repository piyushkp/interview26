"""
Runs your Solver. It's useful to see how Solver is called.
You may want to change how Solver is constructed.
"""

from mazes import get_small_maze
from solver import Solver


def banner(legend: str) -> None:
    border = "#" * (len(legend) + 8)
    print(border)
    print(f"#   {legend}   #")
    print(border)


def main() -> None:
    banner("BEGIN CODE OUTPUT")

    maze = get_small_maze()
    solver = Solver(maze)

    print("Original maze:")
    for row in maze.render():
        print(row)
    print()

    path = solver.solve()
    if path:
        print(f"Path found with {len(path)} steps:")
        print()
        for row in maze.render_with_path(path):
            print(row)
        print()
        print("Path coordinates:")
        for pos in path:
            print(f"  ({pos.row}, {pos.col})")
    else:
        print("No path found!")

    banner("END CODE OUTPUT")


if __name__ == "__main__":
    main()
