#!/usr/bin/python

import PySimpleGUI as sg
import string
import analysis
import matplotlib; matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasAgg
import matplotlib.backends.tkagg as tkagg
import tkinter as Tk

#taken from https://github.com/MikeTheWatchGuy/PySimpleGUI/blob/master/DemoPrograms/Demo_Matplotlib.py
def draw_figure(canvas, figure, loc=(0, 0)):
    """ Draw a matplotlib figure onto a Tk canvas
    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    """
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = Tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)
    return photo


translation_dict = dict()   # Dictionary to translate numbers to letters for plate layout
for number, letter in enumerate(string.ascii_lowercase):
    translation_dict[number] = letter.upper()

header = [[sg.Text('Welcome to Plateau! This application is used to analyze results from 96-well plate assays.')],
          [sg.Text('Please input your data, plate layout and destination to write the results, then press \"Analyze\".')]]

input_fields = [[sg.Text('Data File', size=(15, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='data_file', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Layout File', size=(15, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='layout_file', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Results', size=(15, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='results_file', do_not_clear=True),
                 sg.SaveAs()],
                [sg.Button('Analyze'), sg.Exit()]]

button_grid = [[sg.Text('Click on a button to exclude the value from that well from the analysis.')]]
for row in range(8):
    button_grid.append([])
    for col in range(12):
        identity = translation_dict[row]+str(col+1)
        button_grid[row+1].append(sg.Checkbox(text=identity, font='Fixedsys', key=identity, default=True))

graph = [[sg.Canvas(size=(300, 300), key='canvas')]]

plate_layout_pic = [sg.Graph(canvas_size=(700, 700),
                             graph_bottom_left=(0, 450),
                             graph_top_right=(450, 0),
                             key='_GRAPH_')]


layout = [
            *header,
            *input_fields,
            *button_grid,
            *graph
            #plate_layout_pic,
         ]

window = sg.Window(title='Plateau').Layout(layout)

# g = window.FindElement('_GRAPH_')
# BOX_SIZE = 20
# for row in range(8):
#     for col in range(12):
#         if row is 0 or row is 7 or col is 0 or col is 11:
#             fill = 'grey'
#         else:
#             fill = None
#         g.DrawRectangle(top_left=(col * BOX_SIZE + 5, row * BOX_SIZE + 3),
#                         bottom_right=(col * BOX_SIZE + BOX_SIZE + 5, row * BOX_SIZE + BOX_SIZE + 3),
#                         line_color='black',
#                         fill_color=fill)
#
#         g.DrawText(text=translation_dict[row]+str(col+1),
#                    location=(col * BOX_SIZE + 15, row * BOX_SIZE + 8))


while True:  # Event Loop
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    elif event == 'Analyze':
        figure = analysis.main(data_file=values['data_file'],
                               layout_file=values['layout_file'],
                               results_file=values['results_file'],
                               gui_value_dict=values)
        figure.show(block=False)
        #fig_photo = draw_figure(window.FindElement('canvas').TKCanvas, figure) #TODO: fix this.
window.Close()
