import copy 
import numpy as np

'''

Full description of implementation of algorithm 1 (optimised backtracking):

1. First check if first pass - if yes - find all of the grid locations of currently unassigned variables to search - otherwise, continue. Prevents need
to recompute assignment.
2. If we have a valid solution, return it. We know that the solution will be valid at this step, as we only check consistent assignments, and there are no
variables left to assign, and hence is complete.
3. Otherwise, select the next variable to assign using the MRV with OC heuristic:
    1. Minimum remaining values selects the variable which leaves the fewest assignments for variables it influences.
    2. Only-choice immediately returns a variable if it leaves one assignment (as it is the minimum possible).

4. Remove the current assigned variable from those left to check.
5. Use forward pruning to reduce domain:
    - Generate a list of all the remaining values for a variable to check by removing all of those which are already assigned in the current row,
    column and sub-square of the variable.
6. LCV selects the next value to check (orders values) until all possible values have been exhausted.
    - LCV is implemented by returning the choice of value which leaves the most remaining values for influenced variables in the current row,
    column and sub-square.

7. Check if assigning the selected value to the grid is consistent 
    - Simple to check if consistent by seeing if there are any duplicate values in the current row, column and sub-square of the variable
    assigned.

8. If consistent, recurse with new assignment 
    1. If returns a valid solution - return it
    2. Else - backtrack and try new assignment.

9. If we try every value and cannot find a single consistent assignment for a variable, return invalid solution.

'''

def is_consistent_assignment(i, j, sudoku):
    
    ## Check row i is unique - omitting non-assigned values.
    row = sudoku[i, :]
    row_without_zeroes = row[np.nonzero(row)]
    if len(set(row_without_zeroes)) < len(row_without_zeroes):
        return False
    
    ## Check column j is unique - omitting non-assigned values.
    col = sudoku[:, j]
    col_without_zeroes = col[np.nonzero(col)]
    if len(set(col_without_zeroes)) < len(col_without_zeroes):
        return False
    
    ## Check sub 3x3 box is unique - check which square is container for variable using integer division and multiplication (describe method in report)
    row_start, column_start = (i // 3) * 3, (j // 3) * 3
    square = sudoku[row_start : row_start + 3, column_start : column_start + 3].flatten()
    square_without_zeroes = square[np.nonzero(square)]
    if len(set(square_without_zeroes)) < len(square_without_zeroes):
        return False
    
    return True




def MRV_with_OC(sudoku, unassigned_variables):
    
    ## Initialise assignment to select and variable to keep track of global minimum.
    current_assignment = None
    current_minimum = float("inf")

    for i, j in unassigned_variables:
        
        ## Calculate number of assignments left in row, column, and 3x3 box by counting number of zeroes.

        row = sudoku[i, :]
        assignments_left_in_row = len(np.where(row == 0)[0])
        col = sudoku[:, j]
        assignments_left_in_col = len(np.where(col == 0)[0])

        row_start, column_start = (i // 3) * 3, (j // 3) * 3
        square = sudoku[row_start: row_start + 3, column_start: column_start + 3].flatten()
        assignments_left_in_square = len(np.where(square == 0)[0])

        ## Sum total assignments for affected variables

        total_assignments_left = assignments_left_in_col + assignments_left_in_row + assignments_left_in_square

        ## This is the only-choice circumstance - minimum possible.

        if total_assignments_left == 1:
            return (i, j)
        
        ## Compare to current minimum - if new minimum, update - hence returns global mininum across all possible variables.
        curr = current_minimum
        current_minimum = min(current_minimum, total_assignments_left)
        if current_minimum != curr:
            current_assignment = (i, j)

    
    return current_assignment


def remaining_legal_values(sudoku, i, j):
    # Initialise domain [1, 2, ... , 9] as numpy array.
    domain = np.arange(1, 10)

    row_start, column_start = (i // 3) * 3, (j // 3) * 3

    ## Collect sub-square, row and column.
    square = sudoku[row_start: row_start + 3, column_start: column_start + 3].flatten()
    row = sudoku[i, :]
    col = sudoku[:, j]

    ## Concatenate all values already assigned (we do not have to worry about including duplicates or zeroes)
    assigned_values = np.concatenate((square, row, col))

    ## Create a mask
    mask = ~np.isin(domain, assigned_values)

    ## Filter domain using mask and return as Python list object.
    return list(domain[mask])


def LCV(sudoku, i, j, domain): 

    ## Case of one value in domain - reduced computational work.
    if len(domain) == 1:
        return domain[0]
    
    ## Initialise smallest possible constraints - and current LCV.
    min_constraints = float("inf")
    lcv = None
    
    ## Now the LCV process.
    for value in domain:
        current_constraints = 0
        ## Assign pruned value to copied grid.
        sudoku_cpy = np.copy(sudoku)
        sudoku_cpy[i][j] = value

        ## Get each neighbouring cell in row, column and sub-square.
        
        ### Check row
        for k in range(9):
            current_constraints += len(remaining_legal_values(sudoku_cpy, i, k))

        ### Check column
        for k in range(9):
            current_constraints += len(remaining_legal_values(sudoku_cpy, k, j))


        ### Check sub-square
        row_start, column_start = (i // 3) * 3, (j // 3) * 3
        for a in range(row_start, row_start + 3):
            for b in range(column_start, column_start + 3):
                current_constraints += len(remaining_legal_values(sudoku_cpy, a, b))

        
        cur = min_constraints
        min_constraints = min(current_constraints, min_constraints)
        if min_constraints != cur:
            lcv = value


    return lcv



    

def backtracking_solver(sudoku, unassigned_variables=[]):

    ## Locate all of the non-assigned variables (zeroed states) using np.where().
    if unassigned_variables == []:
        zeroes = np.where(sudoku == 0)
        unassigned_variables = list(zip(zeroes[0], zeroes[1]))


    ## If we find complete solution (no more assignments) can simply return - only consistent assignments considered so far.
    if len(unassigned_variables) == 0:
        return sudoku
    
    ## Otherwise, select the next variable (grid location) with the fewest left possible assignments.
    (i, j) = MRV_with_OC(sudoku, unassigned_variables)

    
    ## Prune assigned variable from search.
    temp_unassigned_vars = copy.copy(unassigned_variables)
    temp_unassigned_vars.remove((i, j))

    ## Forward checking prunes domain.
    pruned_domain = remaining_legal_values(sudoku, i, j)

    ## Checks all values over the forward pruned domain.
    while len(pruned_domain) > 0:

        ## LCV selects best option from pruned domain
        value = LCV(sudoku, i, j, pruned_domain)
        pruned_domain.remove(value)

        ## Temporarily make assignment and check if consistent 
        sudoku[i][j] = value

        if is_consistent_assignment(i, j, sudoku):
            ## If consistent, recurse
            result  = backtracking_solver(sudoku, temp_unassigned_vars)

            ## If solution is not invalid, return it
            if not np.array_equal(result, np.full((9, 9), -1)):
                return result
            
            ## If solution is invalid, undo assignment (backtrack)
            else:   
                sudoku[i][j] = 0

    return np.full((9, 9), -1)


def x_solver(sudoku, unassigned_variables=[]):
    pass


def valid(sudoku):
    temp = list(sudoku.flatten())
    print("This is the flattened sudoku: ", temp)
    for cell in temp:
        try:
            cell = int(cell)
            print(f"Checking cell {cell}")
            if cell not in range(0, 10):
                return False

        except ValueError:
            return False
        


    for i in range(9):
        for j in range(9):
            if not is_consistent_assignment(i, j, sudoku):
                return False

    return True





def solve(solver, sudoku):
    if valid(sudoku):
        print("Valid sudoku grid...")
        match solver:
            case "bt":
                return backtracking_solver(sudoku)
            case "x":
                return x_solver(sudoku)
    else:
        print("Sudoku grid is invalid. Please try again.")
        return np.full((9, 9), -1)
