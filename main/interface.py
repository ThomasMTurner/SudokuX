import threading
import tkinter as tk
from solver import solve
import numpy as np


## General GUI configurations
root                  = tk.Tk()
min_height, min_width = 600, 600
previous              = []

## Set root configurations
root.minsize(min_width, min_height)
root.title("SudokuX")


CELLS                 = None
PARALLEL_CELLS        = []
ALGORITHM             = None
FILLS                 = None
PARALLEL_FILLS = []
NUM_OF_PARALLEL_GRIDS = None


def set_algorithm(algorithm_text):
    global ALGORITHM
    match algorithm_text:
        case "Algorithm X":
            if ALGORITHM == "x":
                alg_x_button.config(highlightbackground="green")
                csp_button.config(highlightbackground="red")
                root.update()
            else:
                ALGORITHM = "x"

        case "DFS":
            if ALGORITHM == "bt":
                csp_button.config(highlightbackground="green")
                alg_x_button.config(highlightbackground="red")
                root.update()
            else:
                ALGORITHM = "bt"






## Fills is a numpy array of Sudoku grid with pre-filled values.
def create_sudoku_grid(grid_frame, fills=None, cell_width=3, is_parallel=False):
   if not is_parallel:
        global FILLS
        global CELLS
        fills = FILLS
     
   cells = [[None] * 9 for _ in range(9)]
   no_solution = False


   if fills is not None:
        if np.array_equal(fills, np.full((9,9), -1)):
            no_solution = True
        fills = list(fills)
   
    
   for i in range(9):
        for j in range(9):
            if fills is None:
                cells[i][j] = tk.Entry(grid_frame, width=cell_width, font=("Helvetica", 12))

            elif no_solution:
                cells[i][j] = tk.Entry(grid_frame, width=cell_width, font=("Helvetica", 12), highlightbackground="red")
                
            else:
                cells[i][j] = tk.Entry(grid_frame, width=cell_width, font=("Helvetica", 12), highlightbackground="green")
                cells[i][j].insert(0, str(fills[i][j]))


            cells[i][j].grid(row=i, column=j)


   
   if not is_parallel:
        CELLS = cells
        return grid_frame

   else:
        return grid_frame, cells


def create_parallel_sudoku_grids():
    frames = []
    i = 0
    while i < NUM_OF_PARALLEL_GRIDS:
        frame = tk.Frame(root)
        if len(PARALLEL_FILLS) > 0:
            frame, cells = create_sudoku_grid(grid_frame=frame, fills=PARALLEL_FILLS[i], cell_width=2, is_parallel=True)
        else:
            frame, cells = create_sudoku_grid(grid_frame=frame, cell_width=2, is_parallel=True)

        PARALLEL_CELLS.append(cells)
        frames.append(frame)
        i += 1
    
    return frames


def end():
    print("Exiting program...")
    root.destroy()


def convert_cell(cell):
    value = cell.get()
    if value == '':
        return 0
    else:
        return value


def convert_grid_to_np_array(is_parallel=False):
    if not is_parallel:
        if CELLS is not None:
            entries = [[convert_cell(CELLS[i][j]) for j in range(9)] for i in range(9)]
            return np.array(entries, dtype=int)
        else:
            return None

    else:
        result = []
        if PARALLEL_CELLS is not None:
            for CELL in PARALLEL_CELLS:
                if CELL is not None:
                    entries = [[convert_cell(CELL[i][j]) for j in range (9)] for i in range(9)]
                    result.append(np.array(entries, dtype=int))
                

            return result

        else:
            return None




def clear_sudoku_grid(num_grids=1):
    global FILLS
    global PARALLEL_FILLS
    global PARALLEL_CELLS
    
    FILLS, PARALLEL_FILLS, PARALLEL_CELLS = None, [], []
    clear_window()
    if num_grids == 1:
        normal()    
    else:
        parallel(n=num_grids)


def fill_sudoku_grid(is_parallel=False):
    if not is_parallel:
        global FILLS
        global CELLS
        grid = convert_grid_to_np_array()
        solved_grid = solve(ALGORITHM, grid)
        FILLS = solved_grid
        clear_window()
        normal()

    else:
        global PARALLEL_CELLS
        global PARALLEL_FILLS

        grids = convert_grid_to_np_array(is_parallel=True)

        threads = []

        for i in range(len(grids)):
            thread = threading.Thread(target=lambda: PARALLEL_FILLS.append(solve(ALGORITHM, grids[i])))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()


        clear_window()
        parallel(n=NUM_OF_PARALLEL_GRIDS)

        

    


## Clear window fully
def clear_window(current_widget=root):
   for widget in current_widget.winfo_children():
       if isinstance(widget, tk.Frame):
           widget.pack_forget()
           widget.place_forget()
       elif isinstance(widget, tk.Button):
           widget.pack_forget()
           widget.place_forget()
       else:
           for child in current_widget.winfo_children():
               clear_window(child)

   root.update()


## Return to previous menu
def go_back(previous):
    if len(previous) > 0:
        clear_window()
        temp = previous.pop(-1)
        temp()



## Run appropriate state and set previous menu.
def set_previous_state_and_run(button_text):
    global previous
    clear_window()
    match button_text:
        case "Play":
            previous.append(home)
            play()
        case "Settings":
            previous.append(home)
            settings()
        case "Normal":
            previous.append(play)
            normal()
        case "Parallel":
            previous.append(play)
            parallel_settings()
        case "Play Parallel Mode":
            previous.append(parallel_settings)
            if NUM_OF_PARALLEL_GRIDS is not None:
                parallel(n=NUM_OF_PARALLEL_GRIDS)
            else:
                parallel_settings()



def set_parallel_grids():
    global NUM_OF_PARALLEL_GRIDS
    try:
        num_of_grids = int(parallel_grids_entry.get())
        if num_of_grids in range(2, 5):
            NUM_OF_PARALLEL_GRIDS = num_of_grids
            incorrect_parallel_warning.pack_forget()
        else:
            NUM_OF_PARALLEL_GRIDS = None
            incorrect_parallel_warning.pack(side="bottom")


    except ValueError:
        NUM_OF_PARALLEL_GRIDS = None
        incorrect_parallel_warning.pack(side="bottom")



## Set global widgets
play_button = tk.Button(root, text="Play", width=10, height=2, command=lambda: set_previous_state_and_run(play_button["text"]))
settings_button = tk.Button(root,text="Settings", width=10, height=2, command=lambda: set_previous_state_and_run(settings_button["text"]))
exit_button = tk.Button(root, text="Exit", width=10, height=2, command=end)
normal_button = tk.Button(root, text="Normal", width=10, height=2, command=lambda: set_previous_state_and_run(normal_button["text"]))
parallel_settings_button = tk.Button(root, text="Parallel", width=10, height=2, command=lambda: set_previous_state_and_run(parallel_settings_button["text"]))
parallel_button = tk.Button(root, text="Play Parallel Mode", width=10, height=2, command=lambda: set_previous_state_and_run(parallel_button["text"]))
back_button = tk.Button(root, text="Back", width=10, height=2, command=lambda:go_back(previous))
parallel_frame = tk.Frame(root)
num_of_parallel_grids_text = tk.Label(parallel_frame, text="Number of Parallel Grids: ")
max_parallel_grids_text = tk.Label(parallel_frame, text="Must be 2-4", fg="red")
set_parallel_grids_button = tk.Button(parallel_frame, text="SET", command=set_parallel_grids)
parallel_grids_entry = tk.Entry(parallel_frame, width=3)
incorrect_parallel_warning = tk.Label(parallel_frame, text="Enter any value between 2-4 inclusive", fg="red")

## Widgets specific to Sudoku Grid
grid_functions_frame = tk.Frame(root)
clear_button = tk.Button(grid_functions_frame, text="Clear", width=10, height=2, command=clear_sudoku_grid)
run_button = tk.Button(grid_functions_frame, text="Run", width=10, height=2, command=fill_sudoku_grid)
algorithms_frame = tk.Frame(root)

    
alg_x_button = tk.Button(algorithms_frame, text="Algorithm X", width=10, height=2, command=lambda: set_algorithm(alg_x_button["text"]))
csp_button = tk.Button(algorithms_frame, text="DFS", width=10, height=2, command=lambda: set_algorithm(csp_button["text"]))


def normal():
    clear_window()
    
    ## Expand width of buttons
    run_button.config(width=10, command=fill_sudoku_grid)
    clear_button.config(width=10, command=clear_sudoku_grid)
    alg_x_button.config(width=10)
    csp_button.config(width=10)
    back_button.config(width=10)


    grid = create_sudoku_grid(grid_frame=tk.Frame(root))
    grid.place(y=40, relx=0.25)
    grid_functions_frame.place(y=300, relx=0.4)
    algorithms_frame.place(y=400, relx=0.28)
    run_button.pack(side='top')
    clear_button.pack(side='top')
    alg_x_button.pack(side='left', padx=5)
    csp_button.pack(side='left', padx=5)
    back_button.place(y=500, relx=0.4)




def parallel(n=2):
    clear_window()

    grids = create_parallel_sudoku_grids()
    for i, grid in enumerate(grids):
        match i:
            case 0:
                grid.place(y=10, relx=0.05)
            case 1:
                grid.place(y=10, relx=0.55)
            case 2:
                grid.place(y=250, relx=0.05)
            case 3:
                grid.place(y=250, relx=0.55)

    root.update()
 
    ## Squeeze width of buttons
    run_button.config(width=7, command=lambda: fill_sudoku_grid(is_parallel=True))
    clear_button.config(width=7, command=lambda: clear_sudoku_grid(num_grids=n))
    alg_x_button.config(width=7)
    csp_button.config(width=7)
    back_button.config(width=7)


    grid_functions_frame.place(y=500, relx=0.4)
    algorithms_frame.place(y=500, relx=0)
    run_button.pack(side='left')
    clear_button.pack(side='left')
    alg_x_button.pack(side='left', padx=5)
    csp_button.pack(side='left', padx=5)
    back_button.place(y=500, relx=0.8)

        

def parallel_settings():
    back_button.config(width=10)
    parallel_frame.place(relx=0.25, rely=0.4)
    num_of_parallel_grids_text.pack(side="left")
    parallel_grids_entry.pack(side="left")
    max_parallel_grids_text.pack(side="left")
    set_parallel_grids_button.pack(side="left")
    parallel_button.place(relx=0.4, rely=0.5)
    back_button.place(relx=0.4, rely=0.6)


def play():
    back_button.config(width=10)
    normal_button.place(relx=0.4, rely=0.3)
    parallel_settings_button.place(relx=0.4, rely=0.4)
    back_button.place(relx=0.4, rely=0.5)


def settings():
    pass


def home():
    play_button.place(relx=0.4, rely=0.3)
    settings_button.place(relx=0.4, rely=0.4)
    exit_button.place(relx=0.4, rely=0.5)



def main():
    home()
    root.mainloop()


if __name__ == "__main__":
    main()
