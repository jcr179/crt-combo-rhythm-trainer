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

def addNote(input_type, curr_colors, curr_lefts, curr_tops, curr_rects, rect_w, rect_h):
    print('Called addNote: ', input_type)
    inputs = {"Dir": 0, "X": 1, "A": 2, "Y": 3, "B": 4, "RB": 5, "RT": 6, "LB": 7, "LT": 8}
    curr_colors.append(colors[inputs[input_type]])
    curr_lefts.append(lefts[inputs[input_type]])
    curr_tops.append(tops[inputs[input_type]])
    curr_rects.append(getRect(curr_lefts[-1], curr_tops[-1], rect_w, rect_h))

def clearNote(num_to_pop, curr_colors, curr_lefts, curr_tops, curr_rects):
    for i in range(num_to_pop):
        curr_colors.pop(0)
        curr_lefts.pop(0)
        curr_tops.pop(0)
        curr_rects.pop(0)