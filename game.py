# dependency for pygame requires homebrew for mac users. read readme guide for procedure.
import pygame
import random
from datetime import datetime

"""

An implementation of Tetris. Idea originally from a youtube guide. Link here: https://www.youtube.com/watch?v=zfvxp7PgQ6c

Credits to "Tech With Tim" and freeCodeCamp.org

"""

#### CONSTANTS ####
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 700
BLOCK_SIZE = 30

# Configured at: 10 blocks wide, 20 blocks high.
GRID_WIDTH = 10
GRID_HEIGHT = 20
PLAY_WIDTH = GRID_WIDTH   * BLOCK_SIZE
PLAY_HEIGHT = GRID_HEIGHT * BLOCK_SIZE
GRID_BORDER_WIDTH = 3
NEXT_SHAPE_HEIGHT = 5 * BLOCK_SIZE
NEXT_SHAPE_WIDTH = 5 * BLOCK_SIZE

TOP_LEFT_X = (WINDOW_WIDTH - PLAY_WIDTH) // 2
TOP_LEFT_Y = WINDOW_HEIGHT - PLAY_HEIGHT

# When updating the blocks, this will check if the next block must fall
UPDATE_INTERVAL = 1000

# COLOURS, because non-American spelling.
GRID_BACKGROUND_COLOUR = (34, 47, 62) # these (R,G,B) tuplets represent colours in RGB format, from 0 to 255 brightness.
WINDOW_BACKGROUND_COLOUR = (52, 31, 151)
GRID_BORDER_COLOUR = (29, 209, 161)
TITLE_COLOUR = (10, 189, 227)
FONT_COLOUR = (200, 214, 229)
SHAPE_COLOURS = [(0, 255, 0), (255, 0, 0),\
                (0, 255, 255), (255, 255, 0),\
                (255, 165, 0), (0, 0, 255), (128, 0, 128)] # super basic >_>

# SHAPES time
def fetch_shapes():
    result = []
    
    try:
        shape_file = open("./resources/shapes.txt")

        for line in shape_file.readlines():
            if line == "\n":
                result[-1].append([]) # store in a new rotation
                continue

            if line[0:2] == "//":
                if len(result) > 0:
                    result[-1] = result[-1][:-1] # remove surplus rotation
                    
                result.append([]) # new shape
                result[-1].append([]) # new rotation
                continue

            # store in last shape, last rotation.
            result[-1][-1].append(line[:-1]) # remove newline
        
        shape_file.close()

    except OSError:
        print("Shapes file could not be opened!")

    return result

# for shape information storage and access
SHAPES = fetch_shapes()
SHAPE_NAMES = "SZIOJLT" # DO NOT CHANGE
SHAPE_SEARCH = { shape : pos for pos, shape in enumerate(SHAPE_NAMES) }

#### GAME RUNTIME FUNCTIONS ####

# DISPLAY SETUP AND RENDERING
def create_grid(locked_positions):
    # generates grid data structure, which is a 2D array.
    grid = [ [ GRID_BACKGROUND_COLOUR for _ in range(GRID_WIDTH) ] for _ in range(GRID_HEIGHT) ]

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            # store the coloured blocks
            if (x, y) in locked_positions:
                colour = locked_positions[(x, y)]
                grid[y][x] = colour
                
    return grid

def draw_grid(surface, grid):
    # pygame renders each object (text, rectangle...) separately,
    # dubbed "surfaces", which are then merged to form the complete interface.

    # draw in the gridlines
    sx = TOP_LEFT_X
    sy = TOP_LEFT_Y

    for y in range(1, GRID_HEIGHT):
        pygame.draw.line(surface, FONT_COLOUR, (sx, sy + y * BLOCK_SIZE), (sx + PLAY_WIDTH, sy + y * BLOCK_SIZE))
        for x in range(1, GRID_WIDTH):
            pygame.draw.line(surface, FONT_COLOUR, (sx + x * BLOCK_SIZE, sy), (sx + x * BLOCK_SIZE, sy + PLAY_HEIGHT))

def render_window(surface, grid, next_piece):
    # fills the window background
    surface.fill(WINDOW_BACKGROUND_COLOUR)

    # draw in the title
    if not pygame.font.get_init(): # load up fonts
        pygame.font.init()
    title_font = pygame.font.SysFont("bebasneue", 60, bold=True) # Because.
    main_title_surface = title_font.render("Supa Tetris", True, TITLE_COLOUR)
    surface.blit(main_title_surface, (TOP_LEFT_X + PLAY_WIDTH/2 - (main_title_surface.get_width()/2), BLOCK_SIZE))

    # draw in the playing field
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            pygame.draw.rect(surface, grid[y][x],
                             (TOP_LEFT_X + x*BLOCK_SIZE, TOP_LEFT_Y + y*BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
            # uses colour data in grid array to configure the grid appearance.

    # add a border to the playing field
    pygame.draw.rect(surface, GRID_BORDER_COLOUR, (TOP_LEFT_X, TOP_LEFT_Y, PLAY_WIDTH, PLAY_HEIGHT), GRID_BORDER_WIDTH)
    
    draw_grid(surface, grid)

    # draw next piece text and window
    text_font = pygame.font.SysFont("consolas", 30)
    np_title_surface = text_font.render("Next Piece", True, FONT_COLOUR)
    surface.blit(np_title_surface, ((TOP_LEFT_X + PLAY_WIDTH + WINDOW_WIDTH)/2 - np_title_surface.get_width()/2,
                                    TOP_LEFT_Y))
    
    pygame.display.update() # push the updates to the screen

# GAME LOGIC

# classifying Tetris pieces
class Piece():
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = SHAPES[SHAPE_SEARCH[shape]]
        self.colour = SHAPE_COLOURS[SHAPE_SEARCH[shape]]
        self.rotation = 0
        self.last_action = 'D'

    def rotate(self):
        self.last_action = 'Q'
        self.rotation = (self.rotation + 1) % len(self.shape) # changes to a rotation within range

    def move_left(self):
        self.last_action = 'L'
        self.x -= 1

    def move_right(self):
        self.last_action = 'R'
        self.x += 1

    def move_down(self):
        self.last_action = 'D'
        self.y += 1

    def reverse(self):
        if self.last_action == 'Q':
            self.rotation -= 1
            if self.rotation < 0:
                self.rotation = len(self.shape) - self.rotation

        elif self.last_action == 'L':
            self.x += 1

        elif self.last_action == 'R':
            self.x -= 1

        elif self.last_action == 'D':
            self.y -= 1

def get_shape():
    piece = Piece(GRID_WIDTH//2, 0, random.choice(SHAPE_NAMES))
    # shift the piece out of the display
    positions = convert_shape_format(piece)
    # since positions are recorded on a row-by-row basis, the first and last positions
    # are also the top-most and bottom-most positions.
    height = positions[-1][1] - positions[0][1] + 1

    for _ in range(height): piece.reverse() # shifts the piece up as many times as needed
    return piece

def convert_shape_format(piece):
    positions = []
    layout = piece.shape[piece.rotation]

    buffer_rows = 0
    buffer_columns = 5 # to be minimised
    within_buffer_y = True
    for y, line in enumerate(layout):
        if line == "....." and within_buffer_y:
            buffer_rows += 1
            continue
        within_buffer_y = False # executes once there's no more buffer lines
        
        within_buffer_x = True
        row = list(line)
        for x, column in enumerate(row):
            if column == '0':
                if within_buffer_x:
                    buffer_columns = min(buffer_columns, x)
                within_buffer_x = False
                positions.append((piece.x + x, piece.y + y))

    for i, position in enumerate(positions):
        positions[i] = (position[0] - buffer_columns, position[1] - buffer_rows) # realigns to top corner

    return positions

def valid_space(piece, grid):
    accepted_positions =\
    [ [ (x, y) for y in range(GRID_HEIGHT) if grid[y][x] == GRID_BACKGROUND_COLOUR ] for x in range(GRID_WIDTH) ]
    accepted_positions = [ position for row in accepted_positions for position in row ] # convert to 1D

    #print("I ran, with", len(accepted_positions), "many empty spaces") #testshit

    queried_positions = convert_shape_format(piece) # check these positions

    for position in queried_positions:
        if position not in accepted_positions and position[1] > -1: # the y value is within range
            return False
    return True

def check_lost(positions):
    for position in positions:
        x, y = position
        if y < 1: # stacked too high
            return True
    return False

def run_game(surface):
    locked_positions = {}
    random.seed(datetime.now())
    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27

    while run: # start the game loop
        #print("Running") #testshit
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        if fall_time/UPDATE_INTERVAL > fall_speed:
            fall_time = 0
            current_piece.move_down()
            if not valid_space(current_piece, grid):
                #print("Changing piece") #testshit
                current_piece.reverse()
                change_piece = True
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                #print("Quit command") #testshit
                run = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.move_left()
                    
                elif event.key == pygame.K_RIGHT:
                    current_piece.move_right()
                    
                elif event.key == pygame.K_DOWN:
                    current_piece.move_down()
                    
                elif event.key == pygame.K_UP:
                    current_piece.rotate()

                if not valid_space(current_piece, grid):
                    current_piece.reverse()

        piece_positions = convert_shape_format(current_piece)

        for i in range(len(piece_positions)):
            x, y = piece_positions[i]
            if y > -1:
                grid[y][x] = current_piece.colour

        if change_piece:
            #print("Why") #testshit
            for position in piece_positions:
                locked_positions[(position[0], position[1])] = current_piece.colour
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
        
        render_window(surface, grid, next_piece)

        if check_lost(locked_positions): # after the piece has been locked in place in the code and visually,
            # the game can end.
            #print("Lost game") #testshit
            run = False

    #print("Exited") #testshit
    pygame.display.quit()
        
#### GAME EXECUTION ####
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("TETRIS")

def main(window):
    run_game(window)

main(window)
































