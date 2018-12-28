import re
from scipy.stats import tstd


class Sample:
    def __init__(self, condition):
        self.condition = condition                           # Allows access to higher level data types
        self.plate = self.condition.plate                    # Allows access to higher level data types
        self.experiment = self.condition.plate.experiment    # Allows access to higher level data types
        self.wells = {}
        self.excluded_wells = {}
        self.concentration = None

    def __str__(self):
        if self.condition.is_cells_only():
            return " ".join([self.experiment.__str__() + ":", "Plate", str(self.plate.number) + ",", self.condition.name])

        return " ".join([self.experiment.__str__() + ":", "Plate", str(self.plate.number) + ",", self.condition.name + ",",
                         str(self.concentration) + " nM"])

    def is_empty(self):
        if len(self.wells) is 0:
            return True
        else:
            return False

    def average_od(self):
        if len(self.wells) > 0:
            return sum(self.wells.values()) / len(self.wells)
        else:
            return 0

    def sd_sample(self):
        if len(self.wells) > 1:
            return tstd([float(x) for x in self.wells.values()])
        else:
            return 0

    def sd_propagated(self):

        if self.condition.is_cells_only():
            return self.sd_sample() * 100

        # elif self.sd_sample() == 0:   # Removed 2018-12-28
        #     return 0

        else:
            sd_control = self.experiment.no_treatment_od_sd()
            od_control = self.experiment.no_treatment_od_avg()

            term_1 = (self.sd_sample() / self.average_od())**2
            term_2 = (sd_control / od_control)**2

            sd = (term_1 + term_2)**0.5 * self.viability()

            return sd

    def viability(self):
        return self.average_od() * 100 / self.experiment.no_treatment_od_avg()


class Condition:
    def __init__(self, plate):
        self.name = "not assigned"
        self.plate = plate                      # Allows access to higher level data types
        self.experiment = plate.experiment      # Allows access to higher level data types
        self.samples = {}

    def __str__(self):
        return " ".join([self.experiment.__str__() + ":", "Plate", str(self.plate.number) + ",", self.name])

    def remove_empty_samples(self):
        """This method is used to remove empty sample Objects from control conditions."""
        samples = {}
        for key in self.samples:
            if not self.samples[key].is_empty():
                samples[key] = self.samples[key]
        self.samples = samples

    def is_cells_only(self):
        if re.search('lysis', self.name):
            return False
        elif re.search('cells', self.name):  # returns True if 'cells only' is in the name
            return True

    def is_lysis_control(self):
        if re.search('lysis', self.name):
            return True
        else:
            return False

    def is_control(self):
        if self.is_cells_only():
            return True
        elif self.is_lysis_control():
            return True
        else:
            return False

    def max_concentration(self):
        return max([float(x.concentration) for x in self.samples.values()])

    def min_concentration(self):
        return min([float(x.concentration) for x in self.samples.values()])

    def sort_samples(self):
        sorted_dict = {}
        for key in sorted(self.samples.keys()):
            sorted_dict[key] = self.samples[key]
        return sorted_dict

    def style_parameters(self):
        return {
            'linestyle': 'solid',
            'label': self.name.upper(),
            'capsize': 5,
            'marker': '.',
            'linewidth': 2
        }


class Plate:
    def __init__(self, experiment):
        self.experiment = experiment    # Allows access to higher level data types
        self.conditions = {}
        self.sample_dict = {}
        self.concentrations = []
        self.number = None

    def __str__(self):
        return " ".join([self.experiment.__str__() + ":", "Plate", str(self.number)])

    def max_concentration(self):
        return max([x.max_concentration() for x in self.conditions.values()])

    def min_concentration(self):
        return min([x.min_concentration() for x in self.conditions.values()])

    def sort_conditions(self):
        sorted_dict = {}
        for key in sorted(self.conditions.keys()):
            sorted_dict[key] = self.conditions[key]
        return sorted_dict

    def get_cells_only(self):
        for condition in self.conditions.values():
            if condition.is_cells_only():
                return condition

    def get_lysis_control(self):
        for condition in self.conditions.values():
            if condition.is_lysis_control():
                return condition

    def cells_only_od(self):
        # samples[0] because there is only one sample in a control condition
        return self.get_cells_only().samples[0].average_od()

    def lysis_od(self):
        return self.get_lysis_control().samples[0].average_od()

    def lysis_viability(self):
        return self.get_lysis_control().samples[0].viability()

    def extra_line_style(self):
        return {'xmin': self.min_concentration(),
                'xmax': self.max_concentration(),
                'linestyle': 'dashed',
                'linewidth': 0.5}

    def all_conditions(self):
        conditions = []
        for condition in self.sort_conditions().values():
            if not condition.is_control():
                conditions.append(condition)
        return conditions


class Experiment:
    def __init__(self):
        self.cell_line = ''
        self.passage_number = ''
        self.media = ''
        self.incubation_time = ''
        self.sample_dict = {}
        self.plates = {}
        self.concentrations = []

    def __str__(self):
        if self.cell_line == '':
            self.cell_line = "[Cell line]"

        if self.passage_number == '':
            self.passage_number = "[#]"

        if self.media == '':
            self.media = "[Media]"

        if self.incubation_time == '':
            self.incubation_time = "[Incubation time]"

        return " ".join([self.cell_line, "P" + self.passage_number, self.incubation_time, "incubation in", self.media])

    def max_concentration(self):
        return max([x.max_concentration() for x in self.all_conditions()])

    def min_concentration(self):
        return min([x.min_concentration() for x in self.all_conditions()])

    def sort_conditions(self):
        return sorted(self.all_conditions(), key=lambda x: x.name)

    def get_cells_only_conditions(self):
        cells_only = []
        for plate in self.plates.values():
            for condition in plate.conditions.values():
                if condition.is_cells_only():
                    cells_only.append(condition)
        return cells_only

    def no_treatment_od_avg(self):
        od_values = []
        for condition in self.get_cells_only_conditions():
            for sample in condition.samples.values():
                for od in sample.wells.values():
                    od_values.append(od)
        return sum(od_values) / len(od_values)

    def no_treatment_od_sd(self):
        od_values = []
        for condition in self.get_cells_only_conditions():
            for sample in condition.samples.values():
                for od in sample.wells.values():
                    od_values.append(od)
        return tstd(od_values)

    def get_lysis_conditions(self):
        lysis = []
        for plate in self.plates.values():
            for condition in plate.conditions.values():
                if condition.is_lysis_control():
                    lysis.append(condition)
        return lysis

    def lysis_od_avg(self):
        od_values = []
        for condition in self.get_lysis_conditions():
            for sample in condition.samples.values():
                for od in sample.wells.values():
                    od_values.append(od)
        return sum(od_values) / len(od_values)

    def lysis_sample_sd(self):
        if len(self.get_lysis_conditions()) > 1:
            od_values = []
            for condition in self.get_lysis_conditions():
                for sample in condition.samples.values():
                    for od in sample.wells.values():
                        od_values.append(od)
            return tstd(od_values)

        else:
            return 0

    def lysis_viability(self):
        return self.lysis_od_avg() * 100 / self.no_treatment_od_avg()

    def lysis_sd_propagated(self):
        if self.lysis_sample_sd() == 0:
            return 0

        else:
            sd_control = self.no_treatment_od_sd()
            od_control = self.no_treatment_od_avg()

            term_1 = (self.lysis_sample_sd() / self.lysis_od_avg())**2
            term_2 = (sd_control / od_control)**2

            sd = (term_1 + term_2)**0.5 * self.lysis_viability()

            return sd

    def extra_line_style(self):
        return {'xmin': self.min_concentration(),
                'xmax': self.max_concentration(),
                'linestyle': 'dashed',
                'linewidth': 0.5}

    def all_conditions(self):
        conditions = []
        for plate in self.plates.values():
            for condition in plate.sort_conditions().values():
                if not condition.is_control():
                    conditions.append(condition)
        return conditions
