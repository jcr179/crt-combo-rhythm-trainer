import pygame
from pygame.locals import *
import notes
from textprint import TextPrint
from init_and_fps import *
import overlay
from math import floor 
import os

import sys 
import time 


"""
Constants
"""
surf_x_size = 900
surf_y_size = 600
num_inputs = 9 # Xbox 360 controller : direction, a,b,x,y,lt,rt,lb,rb
#pygame.mixer.pre_init(44100, 16, num_inputs, 4096)

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

app_name = "I wanna hcl 6frc6"
screen, clock = init_screen_and_clock(surf_x_size, surf_y_size, app_name)
fonts = create_fonts([32, 16, 14, 8])
fps = 60



dt = clock.tick(fps)

run = True 

# Joystick
pygame.joystick.init()

# Get ready to print text and initialize start position
textPrint = TextPrint(x_pos=10, y_pos=10)
textPrintStates = TextPrint(x_pos=10, y_pos=400)
textPrintEval = TextPrint(x_pos=10, y_pos=200)

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

prevDir = 5 # direction stick pointed last in numpad notation

# Default arcade layout for now.
gg_button_map = {
    'X' : 'k',
    'A' : 'p',
    'Y' : 's',
    'RB' : 'h',
    'RT' : 'd',
}

# Circular input buffer
# Every frame, increment buf_ptr and add list of whatever inputs were read
# At end of buffer, reset buf_ptr to 0 and begin to overwrite
buf_size = 10
buf_ptr = 0
buffer = ['.']*buf_size

# Handling frames after doing HCL for measuring on a timeline (recv ~= recovery)
post_hcl_frames = 30 # hcl startup + active + recovery frames = 42 but will leave at 30 now because any input past that is irrelevant to hcl 6frc6
post_hcl_buf_ptr = 0
post_hcl_buffer = ['.']*(post_hcl_frames) # +1 so index n corresponds with frame n of hcl
in_hcl = False # flag for if you're in an HCL or not
post_hcl_frame_num = 0
prev_max_post_hcl_state = 0
prev_post_hcl_buffer = ['.']*(post_hcl_frames) # to let last attempt's results persist on display


# States for tracking hcl input and after hcl
fsm_hcl_state = 0
post_hcl_state = 0
prev_fsm_hcl_states = ['.']*buf_size

# frames for frc
frc_frame1 = 16
frc_frame2 = 17

# evaluation
frc_success = False
frc_frame_attempt = 0
dash_gap = 999
second_6_gap = 999
timeline_tick_spacing = 5 # visual aid for reading input timeline's frames, place a mark every X frames
timeline_tick_char = '|'
frc_tick_char = 'X'

"""
In this game, the frames of a move begin the frame after it's executed.
So if you complete an input for a move on frame M, frame 1 of that move is on frame M+1. If it's got 4 frames of startup, it hits
the opponent on frame M+4.

So once the complete input for HCL is found on frame N, its FRC window is frame N+16 and N+17.

However, actually implementing this causes more errors in timing detection in the program than if we said the FRC window was frame N+15 and N+16,
so we can leave it as it is for now.

This is the best we can do in pygame as its clock is based on millisecond accuracy. 
"""

def fsm_hcl(buffer, input_state, input_btns):
    prereqs = ['*', '6', '3', '2', '1', '4', '6']

    print(input_btns)
    if any(prereqs[input_state] in x for x in buffer) and input_state == 0 and '6' in input_btns:
        return 1

    # from 6 to 3 or 2
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 1 and '3' in input_btns:
        return 2
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 1 and '2' in input_btns:
        return 3

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 2 and '2' in input_btns: 
        return 3

    # from 2 to 1 or 4
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 3 and '1' in input_btns:
        return 4
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 3 and '4' in input_btns:
        return 5

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 4 and '4' in input_btns:
        return 5

    # Might jump from state 5 to 6 or 7 depending on if 6k happens on same frame
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 5 and '6' in input_btns:
        return 6
    elif any(prereqs[input_state] in x for x in buffer) and input_state == 5 and '6' in input_btns and 'k' in input_btns:
        return 7

    elif any(prereqs[input_state] in x for x in buffer) and input_state == 6 and 'k' in input_btns:
        return 7

    return input_state

def tick_hcl(frame_num, timeline, input_state, input_btns):

    output_state = input_state
    input_saved = False

    # Have to let go of 6 (or 3 or 9) from HCL
    if input_state == 0 and not any(item in ['3', '6', '9'] for item in input_btns):
        output_state = 1

    # 1st 6
    elif input_state == 1 and '6' in input_btns:
        output_state = 2
        timeline[frame_num] = '6'
        input_saved = True

    # Let go of 6 again to let another 6 be a valid forward dash BEFORE frc
    elif input_state == 2 and not any(item in ['3', '6', '9'] for item in input_btns):
        output_state = 3

    # FRC
    elif input_state == 3 and (set(['p', 'k', 's']).issubset(input_btns) or 
            set(['p', 'k', 'h']).issubset(input_btns) or 
            set(['k', 's', 'h']).issubset(input_btns)):
        if frc_frame1 <= frame_num <= frc_frame2:
            output_state = 4
        if 'f' not in timeline:
            timeline[frame_num] = 'f'
            input_saved = True
        
    # 2nd 6
    elif input_state == 4 and '6' in input_btns:
        try:
            dash1_frame = timeline.index('6')
        except IndexError:
            dash1_frame = 0

        try:
            frc_frame = timeline.index('f')
        except IndexError:
            frc_frame = 0

        if frame_num - dash1_frame <= 10 and frame_num - frc_frame <= 4:
            output_state = 5

        if timeline.count('6') <= 1:
            timeline[frame_num] = '6'
            input_saved = True

    # track frc success regardless of 6frc6 attempt
    if (set(['p', 'k', 's']).issubset(input_btns) or set(['p', 'k', 'h']).issubset(input_btns) or set(['k', 's', 'h']).issubset(input_btns)) and 'f' not in timeline:
        timeline[frame_num] = 'f'
        input_saved = True

    if not input_saved and (frc_frame1 <= frame_num <= frc_frame2):
        timeline[frame_num] = frc_tick_char

    elif not input_saved and frame_num % timeline_tick_spacing:
        timeline[frame_num] = '-'

    elif not input_saved and frame_num % timeline_tick_spacing == 0:
        timeline[frame_num] = timeline_tick_char

    
    
        

    print('FRAME ', frame_num, ': ' + str(input_state))
    print('\tinput_btns: ', input_btns)
    print('\t\t', set(['p', 'k', 's']).issubset(input_btns))
    print('\t\t', set(['p', 'k', 'h']).issubset(input_btns))
    print('\t\t', set(['k', 's', 'h']).issubset(input_btns))

    return timeline, output_state

while run:
    
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
    textPrintStates.reset()
    textPrintEval.reset()
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
    input_btns = []
    for button_num in xb_button_map:
        button = joystick.get_button(button_num)

        if button and button_num in xb_valid_button_nums:
            input_btns.append(gg_button_map.get(xb_button_map[button_num], ''))

            textPrint.print(screen, "{}".format(xb_button_map[button_num]))
            screen.blit(overlay_btn, [overlay_x+overlay_map[button_num][0], overlay_y+overlay_map[button_num][1]])
            xb_held_buttons[xb_button_map[button_num]] += 1
            print(xb_held_buttons[xb_button_map[button_num]], xb_button_map[button_num])


    axis = round(axis, 3)

    if axis == 0.996:
        input_btns.append(gg_button_map.get('LT', ''))

        textPrint.print(screen, "{}".format(xb_axis_map[axis]))
        screen.blit(overlay_btn, [overlay_x+overlay_map[axis][0], overlay_y+overlay_map[axis][1]])
        xb_held_buttons[xb_axis_map[axis]] += 1
        print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])
    elif axis == -0.996:
        input_btns.append(gg_button_map.get('RT', ''))

        textPrint.print(screen, "{}".format(xb_axis_map[axis]))
        screen.blit(overlay_btn, [overlay_x+overlay_map[axis][0], overlay_y+overlay_map[axis][1]])
        xb_held_buttons[xb_axis_map[axis]] += 1
        print(xb_held_buttons[xb_axis_map[axis]], xb_axis_map[axis])   

    # Get directional input
    hat = joystick.get_hat(0)
    textPrint.print(screen, "{}".format(xb_dir_map[hat]))

    input_btns.append(str(xb_dir_map[hat]))

    textPrint.print(screen, "{}".format("".join([str(item) for item in input_btns])))
    
    # TODO fix for hold directions ; charge moves
    if xb_dir_map[hat] != 5 and xb_dir_map[hat] != prevDir:
        pass

    screen.blit(overlay_balltop, [overlay_x+overlay_map[hat][0], overlay_y+overlay_map[hat][1]])
    prevDir = xb_dir_map[hat]
     
    """ End Xbox 360 """


    """ Start Buffer input processing """
    buffer[buf_ptr] = input_btns
    if buf_ptr == 0:
        buffer[0].append('*') # Special case for beginning to detect HCL

    prev_fsm_hcl_states[buf_ptr] = fsm_hcl_state

    if fsm_hcl_state < 7: # If not currently in an HCL
        fsm_hcl_state = fsm_hcl(buffer, fsm_hcl_state, input_btns)
        if all(fsm_hcl_state == x for x in prev_fsm_hcl_states):
            fsm_hcl_state = 0

    buf_ptr = (buf_ptr + 1) % buf_size

    if fsm_hcl_state == 7: # You're in an HCL
        #if post_hcl_frame_num == 0:
        #    post_hcl_frame_num = 1

        post_hcl_buffer, post_hcl_state = tick_hcl(post_hcl_frame_num, post_hcl_buffer, post_hcl_state, input_btns)

        post_hcl_frame_num += 1

        prev_max_post_hcl_state = max(prev_max_post_hcl_state, post_hcl_state)

        if post_hcl_frame_num < post_hcl_frames:
            textPrintEval.print(screen, "Inputs after HCL {}".format("".join(post_hcl_buffer)))

        #if post_hcl_frame_num >= post_hcl_frames:
        else:
            # Look for next hcl
            fsm_hcl_state = 0

            # Flush post hcl buffer and reset post hcl state
            if 'f' in post_hcl_buffer and frc_frame1 <= post_hcl_buffer.index('f') <= frc_frame2:
                frc_success = True
            else:
                frc_success = False

            if 'f' in post_hcl_buffer:
                frc_frame_attempt = post_hcl_buffer.index('f')
            else:
                frc_frame_attempt = 999

            if post_hcl_buffer.count('6') == 2:
                dash_frames = [index for index, char in enumerate(post_hcl_buffer) if char == '6']
                dash_gap = dash_frames[1] - dash_frames[0]
                second_6_gap = dash_frames[1] - frc_frame_attempt

            else:
                dash_gap = 999
                second_6_gap = 999

            prev_post_hcl_buffer = post_hcl_buffer.copy()
            post_hcl_buffer = ['.']*post_hcl_frames
            post_hcl_state = 0
            post_hcl_frame_num = 0
            prev_max_post_hcl_state = 0
    

    textPrintStates.print(screen, "fsm_hcl_state {}".format(str(fsm_hcl_state)))
    textPrintStates.print(screen, "buf {}".format(buffer))
    textPrintStates.print(screen, "prev_fsm_hcl_states {}".format(prev_fsm_hcl_states))
    textPrintStates.print(screen, "post_hcl_state {}".format(post_hcl_state))
    textPrintStates.print(screen, "prev_max_post_hcl_state {}".format(prev_max_post_hcl_state))

    #textPrintEval.print(screen, "Inputs after HCL {}".format("".join(post_hcl_buffer)))

    if fsm_hcl_state != 7:
        textPrintEval.print(screen, "Inputs after HCL {}".format("".join(prev_post_hcl_buffer)))
    textPrintEval.print(screen, "FRC frame ({}f <= t <= {}f): {}".format(str(frc_frame1), str(frc_frame2), str(frc_frame_attempt)))
    textPrintEval.print(screen, "Dash input gap (<=10f): {}f".format(str(dash_gap)))
    textPrintEval.print(screen, "2nd 6 input gap (<=4f): {}f".format(str(second_6_gap)))
    if frc_success:
        textPrintEval.print(screen, "ROMANTIC! FRC SUCCESS")
    if dash_gap <= 10:
        textPrintEval.print(screen, "NICE! Dash gap SUCCESS")
        if second_6_gap <= 4:
            textPrintEval.print(screen, "YOU ROCK! HCL 6FRC6 SUCCESS!!!")
    
    """ End Buffer input processing """


    display_fps(fonts)

    #pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(0, surf_y_size-300, surf_x_size, 5))

    pygame.display.update()
    clock.tick(fps)

    buttonPressed = False 
    buttonReleased = False

        

        