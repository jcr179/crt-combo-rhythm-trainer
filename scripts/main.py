import pygame
from pygame.locals import *
import notes
from textprint import TextPrint
from init_and_fps import *
import overlay
from math import floor 
import os

"""
Constants
"""
surf_x_size = 600
surf_y_size = 800
num_inputs = 9 # Xbox 360 controller : direction, a,b,x,y,lt,rt,lb,rb

left_offset = 10
top_offset = 10

rect_width = (surf_x_size - left_offset) // num_inputs
rect_height = 10 # default height in case of tap note

#colors = [(128, 128, 128), (255, 0, 0), (255, 165, 0), (255, 255, 0), (128, 255, 0), (0, 128, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]
colors = [(128, 128, 128), (255, 255, 0), (255, 128, 0), (255, 0, 0), (255, 51, 255), (153, 51, 255), (51, 51, 255), (255, 153, 153), (153, 153, 255)]
lefts = [x for x in range(left_offset, surf_x_size-rect_width, rect_width)]
tops = [top_offset]*num_inputs
notes.initNotes(colors, lefts, tops, rect_width, rect_height)
curr_colors = []
curr_lefts = []
curr_tops = [] 
curr_rects = []
arrow_start_x = left_offset 
arrow_start_y = top_offset

xb_button_map = {0: "A", 1: "B", 2: "X", 3: "Y", 4: "LB", 5: "RB", 6: "Back", 7: "Start", 8: "L3", 9: "R3"}
xb_valid_button_nums = set([0, 1, 2, 3, 4, 5])
xb_axis_map = {-0.996: "RT", 0.996: "LT"}
xb_dir_map = {(0, 0): 5, (1, 0): 6, (0, -1): 2, (-1, 0): 4, (0, 1): 8, (1, -1): 3, (-1, -1): 1, (-1, 1): 7, (1, 1): 9}
xb_held_axes = {"LT": False, "RT": False}
xb_axis_released = ""
# LT+RT not supported; this gives same reading as no triggers pressed
xb_held_buttons = {}
for val in xb_button_map.values():
    xb_held_buttons[val] = -1
for val in xb_axis_map.values():
    xb_held_buttons[val] = -1

xb_held_buttons_frames = {}
for val in xb_button_map.values():
    xb_held_buttons_frames[val] = 0
for val in xb_axis_map.values():
    xb_held_buttons_frames[val] = 0

app_name = "CRT v0.1"
screen, clock = init_screen_and_clock(surf_x_size, surf_y_size, app_name)
fonts = create_fonts([32, 16, 14, 8])
fps = 60



dt = clock.tick(fps)
vx = 0.0
vy = 0.6 # at vy=0.1, windows when creating nodes = windows when playing notes with no rect height scaling factor
run = True 

# Joystick
pygame.joystick.init()

# Get ready to print text and initialize start position
textPrint = TextPrint(x_pos=10, y_pos=50)

buttonPressed = False 
buttonReleased = False


debug = False

# Overlay (x360, fightstick). Base dimensions are 539x262
overlay_base, overlay_btn, overlay_balltop = overlay.initOverlay(300, 300, screen)
overlay_rotate_deg = 0.0
overlay_scale_factor = 0.5
overlay_base = pygame.transform.rotozoom(overlay_base, overlay_rotate_deg, overlay_scale_factor)
overlay_btn = pygame.transform.rotozoom(overlay_btn, overlay_rotate_deg, overlay_scale_factor)
overlay_balltop = pygame.transform.rotozoom(overlay_balltop, overlay_rotate_deg, overlay_scale_factor)
overlay_map = {
    0: [176, 175],      # A
    1: [256, 145],      # B
    2: [193, 87],       # X
    3: [271, 52],       # Y
    4: [445, 52],       # LB
    5: [359, 52],       # RB
    0.996: [428, 146],  # LT
    -0.996: [342, 145], # RT
    (0,0): [35, 109],   # neutral
    (0,1): [35, 84],    # up
    (0,-1): [35, 134],  # down 
    (1,0): [63, 109],   # forward 
    (-1,0): [7, 109],   # back
    (1,1): [63, 84],   # up forward
    (-1,-1): [7, 134],   # down back
    (-1,1): [7, 84],   # up back 
    (1,-1): [63, 134]    # down forward
}
for key, val in overlay_map.items():
    overlay_map[key] = (val[0]*overlay_scale_factor, val[1]*overlay_scale_factor)
overlay_x = 300
overlay_y = 50

# Stepmania arrows for direction
img_dir = os.path.join(os.getcwd(), "resources", "images")
arrow_scale_factor = 0.5 # vy 0.4 and scale 0.75 and vertical offset 32
arrow_vertical_spawn_offset = 64
arrow_dir = os.path.join(img_dir, "USWdefault9SM5")

arrows = {1: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_downback.png")), 0.0, arrow_scale_factor),
          2: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_down.png")), 0.0, arrow_scale_factor),
          3: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_downfwd.png")), 0.0, arrow_scale_factor),
          4: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_back.png")), 0.0, arrow_scale_factor),
          6: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_fwd.png")), 0.0, arrow_scale_factor),
          7: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_upback.png")), 0.0, arrow_scale_factor),
          8: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_up.png")), 0.0, arrow_scale_factor),
          9: pygame.transform.rotozoom(pygame.image.load(os.path.join(arrow_dir, "arrow_upfwd.png")), 0.0, arrow_scale_factor)
}





prevDir = 5 # direction stick pointed last in numpad notation

tap_window = 8 # buttons held for longer than this many frames become holds

mode = "rec" # or "play"

while run:
    rectsLeavingThisFrame = 0
    #how to get release or display stick
    for event in pygame.event.get():
         
        if event.type == QUIT: 
            run = False

        if event.type == pygame.JOYBUTTONDOWN:
            print("Joystick button pressed:", event.button)
            xb_held_buttons[xb_button_map[event.button]] = 0

        elif event.type == pygame.JOYBUTTONUP:
            print("Joystick button released:", event.button)
            xb_held_buttons_frames[xb_button_map[event.button]] = xb_held_buttons[xb_button_map[event.button]]
            xb_held_buttons[xb_button_map[event.button]] = -1

        elif event.type == pygame.JOYAXISMOTION:
            axisValue = round(event.value, 3)
            if event.axis == 2 and axisValue == -0.996:
                print("Joystick button pressed: RT")
                xb_held_axes["RT"] = True
                xb_held_buttons[xb_axis_map[axisValue]] = 0
            elif event.axis == 2 and axisValue == 0.0 and xb_held_axes["RT"]:
                print("Joystick button released: RT")
                xb_held_axes["RT"] = False
                xb_axis_released = "RT"
                xb_held_buttons_frames[xb_axis_released] = xb_held_buttons[xb_axis_map[-0.996]]
                xb_held_buttons[xb_axis_map[-0.996]] = -1
            if event.axis == 2 and axisValue == 0.996:
                print("Joystick button pressed: LT")
                xb_held_axes["LT"] = True 
                xb_held_buttons[xb_axis_map[axisValue]] = 0
            elif event.axis == 2 and axisValue == 0.0 and xb_held_axes["LT"]:
                print("Joystick button released: LT")
                xb_held_axes["LT"] = False 
                xb_axis_released = "LT"
                xb_held_buttons_frames[xb_axis_released] = xb_held_buttons[xb_axis_map[0.996]]
                xb_held_buttons[xb_axis_map[0.996]] = -1

        elif event.type == pygame.JOYHATMOTION:
            print("Direction ", xb_dir_map[event.value])
    
    textPrint.reset()
    screen.fill((0, 0, 0)) # put before drawing

    screen.blit(overlay_base, [overlay_x, overlay_y])

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
                textPrint.print(screen, "Hat {} value: {}".format(i, hat))
            textPrint.unindent()
    
            textPrint.unindent()

    # Have only 1 plugged in when starting, TODO make a class and put this into a library, call all these checks
    """ Begin Xbox 360 """
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    name = joystick.get_name()
    textPrint.print(screen, "{}".format(name))

    axis = joystick.get_axis(2)

    buttons = joystick.get_numbuttons()
    for button_num in xb_button_map:
        button = joystick.get_button(button_num)
        if button and button_num in xb_valid_button_nums:
            textPrint.print(screen, "{}".format(xb_button_map[button_num]))
            screen.blit(overlay_btn, [overlay_x+overlay_map[button_num][0], overlay_y+overlay_map[button_num][1]])
            xb_held_buttons[xb_button_map[button_num]] += 1
            print(xb_held_buttons[xb_button_map[button_num]], xb_button_map[button_num])
        if not button and xb_held_buttons_frames[xb_button_map[button_num]]:
            if xb_held_buttons_frames[xb_button_map[button_num]] > tap_window:
                notes.addNote(xb_button_map[button_num], curr_colors, curr_lefts, curr_tops, curr_rects, rect_w=rect_width, rect_h=xb_held_buttons_frames[xb_button_map[button_num]] * (vy/0.1))
            else:
                notes.addNote(xb_button_map[button_num], curr_colors, curr_lefts, curr_tops, curr_rects, rect_w=rect_width, rect_h=rect_height)
            xb_held_buttons_frames[xb_button_map[button_num]] = 0


    axis = round(axis, 3)

    if axis == 0.996:
        textPrint.print(screen, "{}".format(xb_axis_map[axis]))
        screen.blit(overlay_btn, [overlay_x+overlay_map[axis][0], overlay_y+overlay_map[axis][1]])
        xb_held_buttons[xb_axis_map[axis]] += 1
        print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])
    elif axis == -0.996:
        textPrint.print(screen, "{}".format(xb_axis_map[axis]))
        screen.blit(overlay_btn, [overlay_x+overlay_map[axis][0], overlay_y+overlay_map[axis][1]])
        xb_held_buttons[xb_axis_map[axis]] += 1
        print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])        
    elif axis in (0.0, -0.0) and xb_axis_released:
        if xb_held_buttons_frames[xb_axis_released] > tap_window:
            notes.addNote(xb_axis_released, curr_colors, curr_lefts, curr_tops, curr_rects, rect_w=rect_width, rect_h=xb_held_buttons_frames[xb_axis_released] * (vy/0.1))
        else:
            notes.addNote(xb_axis_released, curr_colors, curr_lefts, curr_tops, curr_rects, rect_w=rect_width, rect_h=rect_height)
        xb_axis_released = ""

    hat = joystick.get_hat(0)
    textPrint.print(screen, "{}".format(xb_dir_map[hat]))
    # TODO fix for hold directions ; charge moves
    if xb_dir_map[hat] != 5 and xb_dir_map[hat] != prevDir:
        notes.addNote("Dir", curr_colors, curr_lefts, curr_tops, curr_rects, rect_w=rect_width, rect_h=rect_height, direction=xb_dir_map[hat])
    screen.blit(overlay_balltop, [overlay_x+overlay_map[hat][0], overlay_y+overlay_map[hat][1]])
    prevDir = xb_dir_map[hat]

     
    """ End Xbox 360 """


    for j in range(len(curr_rects)):
        if isinstance(curr_rects[j], pygame.Rect):
            curr_rects[j].left += int(vx*dt)
            curr_rects[j].top += int(vy*dt)
            pygame.draw.rect(screen, curr_colors[j], curr_rects[j])
            if curr_rects[j].top > surf_y_size:
                rectsLeavingThisFrame += 1

        else: # is image
            curr_colors[j][0] += int(vx*dt)
            curr_colors[j][1] += int(vy*dt)
            screen.blit(arrows[curr_rects[j]], [curr_colors[j][0], curr_colors[j][1] - arrow_vertical_spawn_offset])
            if curr_colors[j][1] > surf_y_size:
                rectsLeavingThisFrame += 1

        

    notes.clearNote(rectsLeavingThisFrame, curr_colors, curr_lefts, curr_tops, curr_rects)

    textPrint.print(screen, "Rects in memory: {}".format(str(len(curr_rects))))

    display_fps(fonts)

    # draw judgment line , TODO put into library later
    judgmentLineDistFromBottom = 100
    pygame.draw.line(screen, (255, 255, 255), (0, surf_y_size-judgmentLineDistFromBottom), (surf_x_size, surf_y_size-judgmentLineDistFromBottom), 3)

    pygame.display.update()
    clock.tick(fps)

    buttonPressed = False 
    buttonReleased = False

    # terminate when 1 rect leaves screen, for debugging
    """
    if r.left > surf_x_size or r.top > surf_y_size:
        run = False 
    """


        

        