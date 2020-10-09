import pygame
from pygame.locals import *
import rect_animation

surf_x_size = 600
surf_y_size = 1000
num_inputs = 9 # Xbox 360 controller : direction, a,b,x,y,lt,rt,lb,rb

left_offset = 10
top_offset = 10

rect_width = (surf_x_size - left_offset) // num_inputs
rect_height = 20

colors = [(255, 255, 255), (255, 0, 0), (255, 165, 0), (255, 255, 0), (128, 255, 0), (0, 128, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]
lefts = [x for x in range(left_offset, surf_x_size-rect_width, rect_width)]
tops = [top_offset]*num_inputs

def addNote(input_type, curr_colors, curr_lefts, curr_tops, curr_rects):
    inputs = {"Dir": 0, "X": 1, "A": 2, "Y": 3, "B": 4, "RB": 5, "RT": 6, "LB": 7, "LT": 8}
    curr_colors.append(colors[inputs[input_type]])
    curr_lefts.append(lefts[inputs[input_type]])
    curr_tops.append(tops[inputs[input_type]])
    curr_rects.append(rect_animation.getRect(curr_lefts[-1], curr_tops[-1], rect_width, rect_height))



class TextPrint(object):
    """
    This is a simple class that will help us print to the screen
    It has nothing to do with the joysticks, just outputting the
    information.
    """
    def __init__(self, x_pos=10, y_pos=10):
        """ Constructor """
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_reset_pos = self.x_pos 
        self.y_reset_pos = self.y_pos
        self.reset()
        self.font = pygame.font.SysFont("Arial", 20)
 
    def print(self, my_screen, text_string):
        """ Draw text onto the screen. """
        text_bitmap = self.font.render(text_string, True, (255,255,255))
        my_screen.blit(text_bitmap, [self.x_pos, self.y_pos])
        self.y_pos += self.line_height
 
    def reset(self):
        """ Reset text to the top of the screen. """
        self.x_pos = self.x_reset_pos
        self.y_pos = self.y_reset_pos
        self.line_height = 15
 
    def indent(self):
        """ Indent the next line of text """
        self.x_pos += 10
 
    def unindent(self):
        """ Unindent the next line of text """
        self.x_pos -= 10

def init_screen_and_clock(surf_x_size, surf_y_size):
    global screen, display, clock
    pygame.init()
    WINDOW_SIZE = (surf_x_size, surf_y_size)
    pygame.display.set_caption('CRT v0.1')
    screen = pygame.display.set_mode(WINDOW_SIZE, 0, 32)
    clock = pygame.time.Clock()

def create_fonts(font_sizes_list):
    #"Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts
 
 
def render(fnt, what, color, where):
    #"Renders the fonts as passed from display_fps"
    text_to_show = fnt.render(what, 0, pygame.Color(color))
    screen.blit(text_to_show, where)
 
 
def display_fps():
    #"Data that will be rendered and blitted in _display"
    render(
        fonts[0],
        what=str(int(round(clock.get_fps()))) + " fps",
        color="white",
        where=(0, 0))



init_screen_and_clock(surf_x_size, surf_y_size)
fonts = create_fonts([32, 16, 14, 8])

#DISPLAYSURF = pygame.display.set_mode((surf_x_size, surf_y_size)) 
# returns pygame.Surface object for the window and sets window size in pixels

fps = 60

i = 1
r = rect_animation.getRect(i, i, 20, 20)

#clock = pygame.time.Clock()
dt = clock.tick(fps)
vx = 0.0
vy = 0.08
run = True 

# Joystick
pygame.joystick.init()

# Get ready to print text 
textPrint = TextPrint(x_pos=10, y_pos=50)

iteration = 0

debug = False 

xb_button_map = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "LB", 5: "RB", 6: "Back", 7: "Start", 8: "L3", 9: "R3"}
xb_axis_map = {-0.996: "RT", 0.996: "LT"}
xb_dir_map = {'(0, 0)': 5, '(1, 0)': 6, '(0, -1)': 2, '(-1, 0)': 4, '(0, 1)': 8, '(1, -1)': 3, '(-1, -1)': 1, '(-1, 1)': 7, '(1, 1)': 9}

curr_colors = []
curr_lefts = []
curr_tops = [] 
curr_rects = []

while run: # often used for main game loop: handle events, update game state, draw state to screen
    iteration += 1

    for event in pygame.event.get():
         
        if event.type == QUIT: 
            run = False

        if debug:
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
                print(iteration)
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")
                print(iteration)
    
    textPrint.reset()
    screen.fill((0, 0, 0)) # put before drawing

    if debug: 
        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()
    
        textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
        textPrint.indent()
    
        joystick = pygame.joystick.Joystick(0)
        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
    
            textPrint.print(screen, "Joystick {}".format(i))
            textPrint.indent()
    
            # Get the name from the OS for the controller/joystick
            name = joystick.get_name()
            textPrint.print(screen, "Joystick name: {}".format(name))
    
            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()
            textPrint.print(screen, "Number of axes: {}".format(axes))
            textPrint.indent()
    
            for i in range(axes):
                axis = joystick.get_axis(i)
                textPrint.print(screen, "Axis {} value: {:>6.3f}".format(i, axis))
            textPrint.unindent()
    
            buttons = joystick.get_numbuttons()
            textPrint.print(screen, "Number of buttons: {}".format(buttons))
            textPrint.indent()
    
            for i in range(buttons):
                button = joystick.get_button(i)
                textPrint.print(screen, "Button {:>2} value: {}".format(i, button))
            textPrint.unindent()
    
            # Hat switch. All or nothing for direction, not like joysticks.
            # Value comes back in an array.
            hats = joystick.get_numhats()
            textPrint.print(screen, "Number of hats: {}".format(hats))
            textPrint.indent()
    
            for i in range(hats):
                hat = joystick.get_hat(i)
                textPrint.print(screen, "Hat {} value: {}".format(i, str(hat)))
            textPrint.unindent()
    
            textPrint.unindent()

    # Have only 1 plugged in when starting
    """ Begin Xbox 360 """
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    name = joystick.get_name()
    textPrint.print(screen, "{}".format(name))

    axis = joystick.get_axis(2)

    buttons = joystick.get_numbuttons()
    for button_num in xb_button_map:
        button = joystick.get_button(button_num)
        if button:
            textPrint.print(screen, "{}".format(xb_button_map[button_num]))
            addNote(xb_button_map[button_num], curr_colors, curr_lefts, curr_tops, curr_rects)

    # TODO: for xbox 360, need to handle button state to be able to handle LT+RT
    axis = round(axis, 3)
    if axis == 0.996 or axis == -0.996:
        textPrint.print(screen, "{}".format(xb_axis_map[axis]))
        addNote(xb_axis_map[axis], curr_colors, curr_lefts, curr_tops, curr_rects)
        
    hat = joystick.get_hat(0)
    textPrint.print(screen, "{}".format(xb_dir_map[str(hat)]))
    if xb_dir_map[str(hat)] != 5:
        addNote("Dir", curr_colors, curr_lefts, curr_tops, curr_rects)


     
    """ End Xbox 360 """

    #r1 = r
    r = r.move(vx*dt, vy*dt)
    #print(r1, ' to ', r)

    for j in range(len(curr_rects)):
        curr_rects[j] = curr_rects[j].move(vx*dt, vy*dt)
        pygame.draw.rect(screen, curr_colors[j], curr_rects[j])

    display_fps()
    pygame.draw.rect(screen, (255,0,255,255), r)

    pygame.display.update()
    #pygame.display.flip()
    clock.tick(fps)

    # terminate when 1 rect leaves screen
    """
    if r.left > surf_x_size or r.top > surf_y_size:
        run = False 
    """


        

        