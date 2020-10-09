import pygame
from pygame.locals import *
import rect_animation

class TextPrint(object):
    """
    This is a simple class that will help us print to the screen
    It has nothing to do with the joysticks, just outputting the
    information.
    """
    def __init__(self):
        """ Constructor """
        self.reset()
        self.x_pos = 10
        self.y_pos = 10
        self.font = pygame.font.SysFont("Arial", 20)
 
    def print(self, my_screen, text_string):
        """ Draw text onto the screen. """
        text_bitmap = self.font.render(text_string, True, (255,255,255))
        my_screen.blit(text_bitmap, [self.x_pos, self.y_pos])
        self.y_pos += self.line_height
 
    def reset(self):
        """ Reset text to the top of the screen. """
        self.x_pos = 10
        self.y_pos = 10
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


surf_x_size = 600
surf_y_size = 1000
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
vy = 0.02
run = True 

# Joystick
pygame.joystick.init()

# Get ready to print text 
textPrint = TextPrint()

iteration = 0
while run: # often used for main game loop: handle events, update game state, draw state to screen
    iteration += 1

    for event in pygame.event.get():
         
        if event.type == QUIT: 
            run = False

        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed.")
            print(iteration)
        if event.type == pygame.JOYBUTTONUP:
            print("Joystick button released.")
            print(iteration)
    
    textPrint.reset()
    screen.fill((0, 0, 0)) # put before drawing

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()
 
    textPrint.print(screen, "Number of joysticks: {}".format(joystick_count))
    textPrint.indent()
 
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

    #r1 = r
    r = r.move(vx*dt, vy*dt)
    #print(r1, ' to ', r)


    display_fps()
    pygame.draw.rect(screen, (255,0,255,255), r)

    #pygame.display.update()
    pygame.display.flip()
    clock.tick(fps)

    if r.left > surf_x_size or r.top > surf_y_size:
        run = False 

print(r)

        

        