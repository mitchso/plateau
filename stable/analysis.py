# Data structure
from analysis_objects import *

# Data processing
import string
import time
import pandas

# Plotting
import matplotlib; matplotlib.use("TkAgg")  # Need this statement to be compatible with Tkinter
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter


def define_experiment(layout_file: str):
    """
    Creates an Experiment object with information from the layout file.
    """

    experiment = Experiment()

    if layout_file is None:
        pass

    else:
        with open(layout_file, 'r') as fname:
            metadata = [line.split(sep='\t')[1] for line in fname.readlines()[1:6]]
            experiment.cell_line = metadata[0]
            experiment.passage_number = metadata[1]
            experiment.media = metadata[2]
            experiment.incubation_time = metadata[3]

    return experiment


def define_plate(experiment: Experiment, plate_num: int, data_file: str):

    plate = Plate(experiment=experiment)
    plate.number = plate_num
    plate.sample_dict = plate_reading_to_dict(plate=read_plate(data_file=data_file))

    return plate


def read_layout(layout_file: str) -> pandas.DataFrame:  # TODO: bugged when used with GUI
    """
    Reads the layout file and returns a pandas dataframe with all conditions and controls
    """

    df = pandas.read_csv(layout_file, sep='\t', skiprows=6)  # Read info from info_file into memory
    df = df.loc[df['Treatment'] != '0']  # Filters out 0's
    df = df.loc[-df['Treatment'].str.contains('^[a-z][0-9]{1,2}$', regex=True, case=False)]  # Filters out leftover well values from the template
    df['Well'] = df['Row'] + df['Column'].map(str)  # Add an extra column called 'Well'

    treatment_table = df.loc[-df['Treatment'].str.contains('cells|lysis', regex=True, case=False)]

    control_table = df.loc[df['Treatment'].isin(['cells only (lysis)', 'cells only', 'cells', 'lysis'])]  # Collect controls
    control_table = control_table.drop(columns='Concentration')
    control_table['Concentration'] = 0

    df = pandas.concat([treatment_table, control_table], sort=True)  # Concat the two tables

    return df


def read_plate(data_file: str) -> list:
    """Reads the .txt data file, removes all junk characters and returns each line in a list."""

    fixed_file = []
    with open(data_file, 'rb') as data_file:
        for line in data_file.readlines():
            fixed_1 = ''.join(filter(lambda x: x in string.printable, str(line)))  # remove non-ascii characters
            fixed_2 = fixed_1.replace('b\'', '')  # remove from start of each line
            fixed_3 = fixed_2.replace('\\t', '\t')  # remove non-ascii tabs
            fixed_4 = fixed_3.replace('\\r\\n\'', '\n')  # remove from end of each line
            if len(fixed_4.strip()) > 0:
                fixed_file.append(fixed_4)  # this should be actually fixed

    return fixed_file


def plate_reading_to_dict(plate: list) -> dict:
    """ Reads data from the plate and converts each well reading to a {well: value} dictionary entry."""

    mydict = {}
    for line in plate:
        try:
            first_column = line.split(sep='\t')[1]
            third_column = line.split(sep='\t')[3]
            if re.match('[A-Z][0-9]{1,2}', first_column):
                well = first_column
                if third_column == 'Outlier':
                    value = line.split(sep='\t')[2]
                elif third_column != 'Outlier':
                    value = line.split(sep='\t')[3]
                mydict[well] = float(value)

        except IndexError:
            pass  # Need this try statement to avoid IndexError on lines with no content

    return mydict


def write_output(outfile: str, experiment: Experiment) -> None:
    """ Writes a tab-separated file with the results from the experiment."""

    with open(outfile, 'w') as outfile:

        outfile.write("Experiment:\t%s\n" % experiment)
        outfile.write("No. of plates:\t%s\n" % len(experiment.plates))
        outfile.write("Conditions:\t"+"\t\n\t".join([x.name for x in experiment.all_conditions()])+"\n")
        outfile.write("Date analyzed (y-m-d):\t%s\n\n" % time.strftime('%Y-%m-%d'))

        outfile.write("Analyzed data (Controls):\n")
        outfile.write("\t\tCells only\t\t\tLysis\n")
        outfile.write("\t\t" + "Mean OD\tViability\tStDev (propagated)\t"*2 + "\n")
        for plate in experiment.plates.values():
            outfile.write("\t".join(["\tPlate " + str(plate.number),
                                     str(round(plate.cells_only_od(), 3)),
                                     "100",
                                     str(round(plate.get_cells_only().samples[0].sd_propagated(), 3)),
                                     str(round(plate.lysis_od(), 3)),
                                     str(round(plate.lysis_viability(), 3)),
                                     str(round(plate.get_lysis_control().samples[0].sd_propagated(), 3))]) + "\n")
        if len(experiment.plates) > 1:
            outfile.write("\t".join(["\tMerge",
                                     str(round(experiment.no_treatment_od_avg(), 3)),
                                     "100",
                                     str(round(experiment.no_treatment_od_sd()*100, 3)),
                                     str(round(experiment.lysis_od_avg(), 3)),
                                     str(round(experiment.lysis_viability(), 3)),
                                     str(round(experiment.lysis_sd_propagated(), 3))]) + "\n")

        outfile.write("\n")
        outfile.write("Analyzed data (Conditions):")

        for plate in experiment.plates.values():
            outfile.write("\n")
            conditions = plate.all_conditions()
            outfile.write("Plate " + str(plate.number) + "\t" + "\t\t".join(x.name for x in conditions) + "\n")
            outfile.write("Concentration\t" + 'Viability\tStDev\t' * len(conditions) + "\n")

            for concentration in sorted(plate.concentrations, reverse=True):
                to_print = [str(concentration)]
                for condition in conditions:
                    viability = condition.samples[concentration].viability()
                    stdev = condition.samples[concentration].sd_propagated()
                    to_print.extend([str(round(viability, 3)), str(round(stdev, 3))])
                outfile.write("\t".join(to_print) + "\n")

        outfile.write("\n")
        outfile.write("Raw data:\n")
        outfile.write("\t".join(["Plate #", "Condition", "Concentration", "Wells", "OD values", "Excluded wells",
                                 "Excluded OD values", "Mean OD", "Viability", "StDev (sample)", "StDev (propagated)"]) + "\n")

        for plate in experiment.plates.values():
            for condition in plate.sort_conditions().values():
                for sample in condition.sort_samples().values():
                    to_print = [plate.number,
                                condition.name,
                                sample.concentration,
                                list(sample.wells.keys())[0],
                                list(sample.wells.values())[0],
                                ", ".join(list(sample.excluded_wells.keys())),
                                ", ".join(map(str, list(sample.excluded_wells.values()))),
                                round(sample.average_od(), 3),
                                round(sample.viability(), 3),
                                round(sample.sd_sample(), 3),
                                round(sample.sd_propagated(), 3)]

                    if len(sample.wells) > 1:
                        for index, key in enumerate(sample.wells):
                            if index is 0:
                                pass
                            else:
                                to_print.append("\n" + "\t"*3 + "\t".join([key, str(sample.wells[key])]))

                    outfile.write("\t".join(map(str, to_print)) + "\n")


def plot_graph(experiment: Experiment):
    """ Plots all of the data from the experiment."""

    plt.clf()
    for condition in experiment.sort_conditions():
        if not condition.is_cells_only() and not condition.is_lysis_control():
            x = [float(sample.concentration) for sample in condition.sort_samples().values()]
            y = [sample.viability() for sample in condition.sort_samples().values()]
            errors = [sample.sd_propagated() for sample in condition.sort_samples().values()]
            plt.errorbar(x, y, yerr=errors, **condition.style_parameters())

    # Stylize the graph
    plt.xscale('log')
    fig, ax = plt.gcf(), plt.gca()  # Get current figure and axes instance
    handles, labels = ax.get_legend_handles_labels()  # Get legend handles and labels
    handles = [h[0] for h in handles]  # Remove error bars from legend handles
    ax.xaxis.set_major_formatter(ScalarFormatter())  # Need this to make the axis numbers display in plain
    ax.yaxis.set_major_formatter(ScalarFormatter())  # rather than scientific notation
    [ax.spines[spine].set_visible(False) for spine in ax.spines  # Remove borders around the top and right side
     if ax.spines[spine].spine_type is 'right'
     or ax.spines[spine].spine_type is 'top']
    ax.tick_params(which='minor', length=4)

    # Extra lines to add
    plt.hlines(100, **experiment.extra_line_style())  # 100% viability line
    plt.hlines(experiment.lysis_viability(), color='red', **experiment.extra_line_style())  # lysis line
    plt.hlines(0, **experiment.extra_line_style())  # 0 line if the origin is not set at 0

    plt.title(str(experiment))
    plt.legend(handles, labels, markerscale=0, frameon=False)  # Add legend

    return plt


def main(data_files: list, layout_files: list, results_file: str, plate_dicts: list):

    experiment = define_experiment(layout_files[0])

    # --------- Define plate(s) --------- #
    for i, layout_file in enumerate(layout_files):
        experiment.plates[i] = define_plate(experiment=experiment, plate_num=i+1, data_file=data_files[i])

        df = read_layout(layout_file)
        conditions = list(set([row[1]['Treatment'] for row in df.iterrows()]))
        concentrations = list(set([row[1]['Concentration'] for row in df.iterrows()]))

        experiment.concentrations = concentrations[:]
        experiment.plates[i].concentrations = concentrations[:]

        try:
            experiment.concentrations.remove(0.0)  # Cleans out any 0's in the concentration list
            experiment.plates[i].concentrations.remove(0.0)  # Cleans out any 0's in the concentration list
        except ValueError:
            pass

        # --------- Define conditions ---------#
        for condition in conditions:
            experiment.plates[i].conditions[condition] = Condition(plate=experiment.plates[i])
            experiment.plates[i].conditions[condition].name = condition

            # --------- Define samples ---------#
            for concentration in experiment.plates[i].concentrations + [0]:  # Add 0 to pick up controls as well
                experiment.plates[i].conditions[condition].samples[concentration] = Sample(condition=experiment.plates[i].conditions[condition])

                for index, row in df.iterrows():
                    if row['Treatment'] == condition and row['Concentration'] == concentration:
                        value = experiment.plates[i].sample_dict[row['Well']]
                        experiment.plates[i].conditions[condition].samples[concentration].concentration = concentration
                        if plate_dicts[i][row['Well']] is True:
                            experiment.plates[i].conditions[condition].samples[concentration].wells[row['Well']] = value
                        if plate_dicts[i][row['Well']] is False:
                            experiment.plates[i].conditions[condition].samples[concentration].excluded_wells[row['Well']] = value

    # --------- Clean up the data ---------#
    for plate in experiment.plates.values():
        for condition in plate.conditions.values():
            condition.remove_empty_samples()

    write_output(outfile=results_file, experiment=experiment)  # Write data to file

    return plot_graph(experiment=experiment)
