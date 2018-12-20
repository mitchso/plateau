import PySimpleGUI as sg
import string
import analysis
import os


def make_button_grid(plate_number: int, translation_dict: dict):
    button_grid = [[sg.Text('Plate %s' % plate_number)]]
    for row in range(8):
        button_grid.append([])
        for col in range(12):
            text = translation_dict[row] + str(col + 1)
            identity = "plate" + str(plate_number) + "_" + translation_dict[row] + str(col + 1)
            button_grid[row + 1].append(sg.Checkbox(text=text, font='Fixedsys', key=identity, default=True))
    return button_grid


def filter_values_dict(values: dict, keyword: str):
    filtered_dict = {}
    for key in values:
        if keyword in str(key):
            new_key = str(key).replace(keyword, '')
            filtered_dict[new_key] = values[key]
    return filtered_dict


def build_translation_dict():
    """ Dictionary to translate numbers to letters for plate layout. """
    tdict = dict()  #
    for number, letter in enumerate(string.ascii_lowercase):
        tdict[number] = letter.upper()
    return tdict

# os.path.dirname(os.path.abspath(__file__))+"/plateau.png" # TODO: debug this
header = [[sg.Image("/Users/mitchsyberg-olsen/github/plateau/plateau.png")],
          [sg.Text('Welcome to Plateau! This application is used to analyze results from 96-well plate assays.',
                   font=('Any', 15))],
          [sg.Text('Please input your data, plate layout and destination to write the results, then press \"Analyze\".',
                   font=('Any', 15))],
          [sg.Text('If you would like to exclude any values from the analysis, navigate to the \"Exclude\" tab.',
                   font=('Any', 15))]]

input_fields = [[sg.Text('Data File 1', size=(20, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='data_file_1', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Layout File 1', size=(20, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='layout_file_1', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Data File 2 (Optional)', size=(20, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='data_file_2', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Layout File 2 (Optional)', size=(20, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='layout_file_2', do_not_clear=True),
                 sg.FileBrowse()],
                [sg.Text('Results', size=(20, 1), auto_size_text=True, justification='right'),
                 sg.InputText('', key='results_file', do_not_clear=True),
                 sg.SaveAs()],
                [sg.Button('Analyze'), sg.Exit()]]

tab2_header = [[sg.Text('This page is for excluding well values from the analysis.')],
               [sg.Text('Any box that is unchecked will no longer be considered.')],
               [sg.Text('NOTE: The program WILL crash if you exclude both technical replicates of a sample.')]]

translation_dict = build_translation_dict()
button_grid_1 = make_button_grid(1, translation_dict)
button_grid_2 = make_button_grid(2, translation_dict)

data_image = sg.Image(filename=os.path.dirname(os.path.abspath(__file__))+"/data_structure.png")
documentation = sg.Text(text="This program was developed by Mitch Syberg-Olsen.\n"
                             "For current documentation, please visit:\n"
                             "https://github.com/mitchso/plateau",
                        font=('Any', 15))


tab1_layout = [*header, *input_fields]
tab2_layout = [*tab2_header, *button_grid_1, *button_grid_2]
tab3_layout = [[documentation]]

full_layout = [[
    sg.TabGroup(
        [[sg.Tab('Analysis', tab1_layout),
          sg.Tab('Exclude', tab2_layout),
          sg.Tab('Documentation', tab3_layout)]]
    )
]]

window = sg.Window(title='Plateau').Layout(full_layout)

while True:  # Event Loop
    event, values = window.Read()

    if event is None or event == 'Exit':
        break

    elif event == 'Analyze':
        data_files = list(filter(None, [values['data_file_1'], values['data_file_2']]))
        layout_files = list(filter(None, [values['layout_file_1'], values['layout_file_2']]))

        if len(data_files) == 0:
            sg.PopupOK('No data file provided.')
        elif len(layout_files) == 0:
            sg.PopupOK('No layout file provided.')
        elif len(data_files) != len(layout_files):
            sg.PopupOK('Number of data files and layout files do not match.')
        elif values['results_file'] == '':
            sg.PopupOK('Please provide a name for the results file.')
        else:
            plate_1_dict = filter_values_dict(values, keyword='plate1_')
            plate_2_dict = filter_values_dict(values, keyword='plate2_')

            try:
                figure = analysis.main(data_files=data_files,
                                       layout_files=layout_files,
                                       results_file=values['results_file'],
                                       plate_dicts=[plate_1_dict, plate_2_dict])
                figure.show(block=False)

            except KeyError:
                sg.PopupOK('Possible error: Excluded both technical replicates of a sample.')

            except Exception:
                sg.PopupOK('Something went wrong. Please check the files provided and try again.')

window.Close()
