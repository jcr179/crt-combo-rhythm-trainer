import pygame

def getRect(left, top, width, height):
    if left >= 0 and top >= 0 and width > 0 and height > 0:
        return pygame.Rect(left, top, width, height)
    else:
        return None

def initNotes(colors_, lefts_, tops_, rect_width_, rect_height_):
    global colors, lefts, tops, rect_width, rect_height 
    colors = colors_
    lefts = lefts_
    tops = tops_
    rect_width = rect_width_
    rect_height = rect_height_

def addNote(input_type, curr_colors, curr_lefts, curr_tops, curr_rects, rect_w, rect_h, direction=None):
    print('Called addNote: ', input_type) # debug
    #inputs = {"Dir": 0, "X": 1, "A": 2, "Y": 3, "B": 4, "RB": 5, "RT": 6, "LB": 7, "LT": 8}
    inputs = {"Dir": 0, "X": 1, "Y": 2, "RB": 3, "A": 4, "B": 5, "RT": 6, "LB": 7, "LT": 8}
    directions = {(0, 0): 5, (1, 0): 6, (0, -1): 2, (-1, 0): 4, (0, 1): 8, (1, -1): 3, (-1, -1): 1, (-1, 1): 7, (1, 1): 9}
    if input_type != "Dir":
        curr_colors.append(colors[inputs[input_type]])
        curr_lefts.append(lefts[inputs[input_type]])
        curr_tops.append(tops[inputs[input_type]])
        curr_rects.append(getRect(curr_lefts[-1], curr_tops[-1], rect_w, rect_h))
    else: # 
        curr_colors.append([lefts[inputs[input_type]], tops[inputs[input_type]]])
        curr_lefts.append(0)
        curr_tops.append(0)
        curr_rects.append(direction)

def clearNote(num_to_pop, curr_colors, curr_lefts, curr_tops, curr_rects):
    for i in range(num_to_pop):
        curr_colors.pop(0)
        curr_lefts.pop(0)
        curr_tops.pop(0)
        curr_rects.pop(0)