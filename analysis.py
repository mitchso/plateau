import os
import re
import string
import pandas
import yaml
from sys import argv
import matplotlib; matplotlib.use("TkAgg")  # Need this statement to be compatible with Tkinter
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
from scipy.stats import variation, tstd


class Sample(object):
    def __init__(self):
        self.name = "not assigned"
        self.wells = []
        self.values = []
        self.treatment = "not assigned"
        self.concentration = 0.0

    def average_od(self):
        return sum(self.values) / len(self.values)

    def cv(self):
        if len(self.values) > 1:
            #return variation(self.values)*100
            return tstd(self.values) * 100
        else:
            return 0

    def viability(self, no_tmt_od: float):
        return self.average_od() * 100 / no_tmt_od


class Condition(object):
    def __init__(self):
        self.name = "not assigned"
        self.samples = []

    def is_control(self):
        if re.search('cells only', self.name):
            return True
        return False

    def max_concentration(self):
        return max([x.concentration for x in self.samples])

    def min_concentration(self):
        return min([x.concentration for x in self.samples])

    def sort_samples(self):
        return sorted(self.samples, key=lambda x: x.concentration)

    def colour(self):
        current_path = os.path.dirname(os.path.realpath(__file__))
        with open(current_path + "/styles.yml", 'r') as infile:
            style_dict = yaml.load(infile)

        try:
            return style_dict['colours'][self.name.lower()]
        except KeyError:
            return None

    def style_parameters(self):
        return {
            'linestyle': 'dashed' if 'pep' not in self.name.lower() else 'solid',
            'label': self.name.upper(),
            'capsize': 5,
            'marker': '.',
            'color': self.colour(),
            'linewidth': 2
        }


class Experiment(object):
    def __init__(self):
        self.name = "not assigned"
        self.cell_line = ""
        self.passage_number = ""
        self.media = ""
        self.incubation_time = ""
        self.conditions = []
        self.controls = []
        self.sample_dict = {}

    def max_concentration(self):
        return max([x.max_concentration() for x in self.conditions])

    def min_concentration(self):
        return min([x.max_concentration() for x in self.conditions])

    def sort_conditions(self):
        return sorted(self.conditions, key=lambda x: x.name)

    def get_controls(self):
        return [condition for condition in self.conditions if condition.is_control()]

    def no_treatment_od(self):
        # samples[0] because there is only one sample in a control condition
        return max(condition.samples[0].average_od() for condition in self.get_controls())

    def lysis_od(self):
        return min(condition.samples[0].average_od() for condition in self.get_controls())

    def lysis_viability(self):
        return min(condition.samples[0].viability(self.no_treatment_od()) for condition in self.get_controls())

    def extra_line_style(self):
        return {'xmin': self.min_concentration(),
                'xmax': self.max_concentration(),
                'linestyle': 'dashed',
                'linewidth': 0.5}


def main(data_file, layout_file, results_file, gui_value_dict):
    experiment = Experiment()

    # Collect metadata
    with open(layout_file, 'r') as fname:
        metadata = [line.split(sep='\t')[1] for line in fname.readlines()[1:6]]
        experiment.cell_line = metadata[0]
        experiment.passage_number = metadata[1]
        experiment.media = metadata[2]
        experiment.incubation_time = metadata[3]

    # Read info from info_file into memory
    info_table = pandas.read_csv(layout_file, sep='\t', skiprows=6)
    treatment_table = info_table.loc[info_table.ne(0).all(axis=1)]
    control_table = info_table.loc[info_table['Treatment'].isin(['cells only (lysis)', 'cells only'])]
    final_table = pandas.concat([treatment_table, control_table])
    final_table['Well'] = final_table['Row']+final_table['Column'].map(str)

    treatments = list(set([row[1]['Treatment'] for row in final_table.iterrows()]))
    concentrations = list(set([row[1]['Concentration'] for row in final_table.iterrows()]))

    # Collect sample information
    for treatment in treatments:
        for concentration in concentrations:
            sample = Sample()
            for index, row in final_table.iterrows():
                if (gui_value_dict[row['Well']] is True
                        and row['Treatment'] == treatment
                        and row['Concentration'] == concentration):
                    sample.treatment = treatment
                    sample.concentration = concentration
                    sample.name = treatment+", "+str(concentration)+" nM"
                    sample.wells.append(row['Well'])
                    experiment.sample_dict[sample.name] = sample

    # Fix weird encoding from old plate reader
    fixed_file = []
    with open(data_file, 'rb') as data_file:
        for line in data_file.readlines():
            fixed_1 = ''.join(filter(lambda x: x in string.printable, str(line)))   # remove non-ascii characters
            fixed_2 = fixed_1.replace('b\'', '')    # remove from start of each line
            fixed_3 = fixed_2.replace('\\t', '\t')  # remove non-ascii tabs
            fixed_4 = fixed_3.replace('\\r\\n\'', '\n')  # remove from end of each line
            fixed_file.append(fixed_4)  # this should be actually fixed

    # Collect info from input file
    for key in experiment.sample_dict:
        for well in experiment.sample_dict[key].wells:
            for line in fixed_file:
                if re.search(well, line):
                    if line.split(sep='\t')[3] == 'Outlier':
                        od_value = line.split(sep='\t')[2]
                    else:
                        od_value = line.split(sep='\t')[3]
                    experiment.sample_dict[key].values.append(float(od_value))

    # Group values into experiment.conditions
    for treatment in treatments:
        condition = Condition()
        condition.name = treatment
        condition.samples = [sample for sample in experiment.sample_dict.values() if sample.treatment is treatment]
        experiment.conditions.append(condition)

    # Write output table
    open(results_file, 'w').close()
    with open(results_file, 'w') as results_file:
        results_file.write("\t".join(["Treatment", "Concentration (nM)", "Wells", "Raw Values", "Mean OD", "Viability", "CV %", "\n"]))
        for condition in experiment.sort_conditions():
            for sample in condition.sort_samples():
                results_file.write("\t".join(str(x) for x in ([sample.treatment,
                                                               sample.concentration,
                                                           ", ".join(str(x) for x in sample.wells),
                                                           ", ".join(str(x) for x in sample.values),
                                                               round(sample.average_od(), 3),
                                                               round(sample.viability(experiment.no_treatment_od()), 3),
                                                               round(sample.cv(), 3),
                                                               "\n"])))

    plt.clf()
    # Add data to graph
    y_offset = 1.0
    for condition in experiment.sort_conditions():
        if not condition.is_control():
            # x = [math.log(sample.concentration*y_offset, 10) for sample in condition.sort_samples()]
            x = [sample.concentration * y_offset for sample in condition.sort_samples()]
            y = [sample.viability(experiment.no_treatment_od()) for sample in condition.sort_samples()]
            errors = [sample.cv() for sample in condition.sort_samples()]
            plt.errorbar(x, y, yerr=errors, **condition.style_parameters())
            #y_offset += 0.01

    # Stylize the graph
    plt.xscale('log')
    fig, ax = plt.gcf(), plt.gca()  # Get current figure and axes instance
    handles, labels = ax.get_legend_handles_labels()  # Get legend handles and labels
    handles = [h[0] for h in handles]  # Remove error bars from legend handles
    ax.xaxis.set_major_formatter(ScalarFormatter())  # Need this to make the axis numbers display in plain
    ax.yaxis.set_major_formatter(ScalarFormatter())         # rather than scientific notation
    [ax.spines[spine].set_visible(False) for spine in ax.spines  # Remove borders around the top and right side
     if ax.spines[spine].spine_type is 'right'
     or ax.spines[spine].spine_type is 'top']
    ax.tick_params(which='minor', length=4)

    plt.hlines(100, **experiment.extra_line_style())  # 100% viability line
    plt.hlines(experiment.lysis_viability(), color='red', **experiment.extra_line_style())  # lysis line
    plt.text(0, experiment.lysis_viability(), 'blah')  # TODO: fix this to show text that reads lysis
    # plt.subplots_adjust(left=0.25)  # TODO: use this to move the plot so that text can fit beside it
    plt.hlines(0, **experiment.extra_line_style())  # 0 line if the origin is not set at 0

    plt.title(" ".join([experiment.cell_line,
                        "P"+experiment.passage_number,
                        experiment.incubation_time,
                        "incubation in",
                        experiment.media]))

    plt.legend(handles, labels, markerscale=0, frameon=False)  # Add legend

    # Finally, display the graph
    return plt

if __name__ == '__main__':
    main(data_file=argv[1],
         layout_file=argv[2],
         results_file=argv[3],
         gui_value_dict='remove_this_')
