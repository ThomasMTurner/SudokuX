# SudokuX
Parallel 9x9 Sudoku solver using algorithm X and optimised backtracking DFS.

## Sudoku directories
"sudoku" contains assignment solution for backtracking depth-first search on 9x9 Sudoku grids. "SudokuX" contains the full GUI, parallelisation and algorithm X as the full project extending the assignment.

## Backtracking DFS
Approach is explained in comments in the main **solver.py** file. A further overview is included in the report.

## Algorithm X
...


## Parallel Solve
Used simple threading techniques provided by the standard Python library. This involved creating n threads for each of the sudoku grids to be solved, and using the solve() function (which processes the grids) as a target. 
