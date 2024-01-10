import sys
import time
import random
import pygame
import pyverilator

# Generate a random board state of alive and dead cells
def generate_initial_board_state(board_size):
    return [[random.randint(0, 1) for _ in range(board_size)] for _ in range(board_size)]

# Read board state from 2D array and convert into integer for Verilog module
def pack_grid_to_int(grid):
    result = 0
    bit_position = 0

    # Iterate through each row and each column in the grid
    for row in grid:
        for value in row:
            # Shift the current result to the left and add the current value
            result |= (value << bit_position)
            bit_position += 1

    return result

# Unpack Verilog modules output into 2D array 
def unpack_int_to_grid(value):
    grid = []
    for row in range(16):
        grid_row = []
        for col in range(16):
            bit_position = row * 16 + col
            bit = (value >> bit_position) & 1
            grid_row.append(bit)
        grid.append(grid_row)
    return grid

# Calls Verilator and drives setup signals for Verilog module
def setup_simulator():
    sim = pyverilator.PyVerilator.build('conways_game_of_life.v')
    sim.io.clk = 0
    sim.io.load = 0
    sim.io.data = 0
    sim.clock.tick()
    return sim

# Draw states of the cells onto board grid
def draw_grid(screen, grid, cell_size):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            color = (0,220,220) if grid[y][x] == 1 else (255, 255, 255)
            pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))

def main():

    # Generate a random board state
    board_size = 16
    initial_board_state = generate_initial_board_state(board_size)
    
    # Pack generated board array for Verilog module input
    packed_data = pack_grid_to_int(initial_board_state)

    # Initialize Verilator simulation
    sim = setup_simulator()

    # Drive setup signals to Verilog module
    sim.io.data = packed_data
    sim.io.load = 1
    sim.clock.tick()
    sim.io.load = 0

    # Initialize pygame
    pygame.init()

    # Express cells in terms of pixels
    cell_size = 50
    width = board_size * cell_size
    height = board_size * cell_size

    # Initialize pygame window
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption('Verilog\'s Game of Life')

    # Main loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Step Verilog module
        sim.clock.tick()

        # Create the next frame
        screen.fill((200, 200, 200))
        grid = unpack_int_to_grid(sim.io.q)
        draw_grid(screen, grid, cell_size)
        pygame.display.flip()
        time.sleep(0.25)
        
if __name__ == '__main__':
    main()