#!/usr/bin/python

import PySimpleGUI as sg
import string
import analysis

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

tab1_layout = [*header, *input_fields, *button_grid]
tab2_layout = [[]]  # TODO: Write documentation
tab3_layout = [[]]  # TODO: include references to necessary literature and dependencies

full_layout = [[sg.TabGroup([[sg.Tab('Analysis', tab1_layout),
                              sg.Tab('Documentation', tab2_layout),
                              sg.Tab('References', tab3_layout)]])]]

window = sg.Window(title='Plateau').Layout(full_layout)

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
window.Close()
