<h6 align="center">source code for:</h6>
<p align="center">
<img align="center" src="https://github.com/mitchso/plateau/blob/master/images/plateau.png" alt="plateau">
</p>
<h6 align="center"> open-source, cross-platform, standalone <br> application for microplate data analysis</h6>

## plateau
- [Introduction](#introduction)
	- [Experimental assumptions](#experimental-assumptions)
- [Installation](#installation)
	- [Mac](#mac)
	- [Windows](#windows)
- [Usage](#usage)
	- [Inputs](#inputs)
	- [Outputs](#outputs)
	- [1 vs 2 plate experiments](#1-vs-2-plate-experiments)
	- [Exclude tab](#exclude-tab)
	- [Usage example](#usage-example)
- [Code overview](#code-overview)
- [Application packaging](#application-packaging)

## Introduction
This is the source code for an application I developed called plateau. It is a pretty straightforward application that is meant to automate the analysis of microplate data from cell-based assays.

As of this moment it can only do one type of analysis and has also only been written with one type of readout file in mind, so there is a pretty good chance this application would have to be adapted if someone else were to use it. 

That being said, feel free to open an issue or submit a pull request if you are interested in using the application and the current version does not suit your needs.

Here's the current look of the application as seen on a Mac:

![Main page](https://github.com/mitchso/plateau/blob/master/images/main_tab.png)

### Experimental assumptions
In order for Plateau to run, the following assumptions must be met:

* Every condition must have the same range of concentrations, for example:
	* You are testing treatments in the range of 100 - 0.1 nM, with dilutions of 100 nM, 10 nM, 1 nM, and 0.1 nM.
	* In this case, Plateau assumes that every condition in your experiment will follow this same dilution scheme.
	* If any condition does not follow the same dilution scheme, plateau will raise an error. 
* Each plate must have at least 1 well with no treatment (named 'cells' or 'cells only')
* Each plate must have at least 1 well that has been lysed as a positive control (named 'lysis' or 'cells only (lysis)')

## Installation

The standalone application can be downloaded from:

```
https://sourceforge.net/projects/plateau/
```

The application can also be run from cloning this repo and calling python3 on the gui.py file like so:

```
git clone https://github.com/mitchso/plateau.git
cd /path/to/repo/
python3 gui.py

```

### Mac
There is a known bug currently with Python 3.7.1 and PyInstaller 3.4, which were used to bundle this standalone application.
In brief, the tkinter/tcl modules are not properly packaged and will not be found by the application when it is executed on your local computer. I have tried manually adding the missing binary files after bundling but unfortunately this still did not solve the issue!

The workaround for this is to install Python 3.7.1 directly from:

```
https://www.python.org/downloads/release/python-371/
```
If you have done this, you should have the correct version of tkinter/tcl visible to the application and it should run without problems. This worked for me when deploying the application onto a different mac, but it is definitely not an optimal solution.

### Windows
Installation for windows appears to work without bugs. Simply go to 
```
https://sourceforge.net/projects/plateau/
```
and install the latest release.

## Usage

### Inputs
Plateau takes 1-2 pairs of data & layout files. 
<br>
<b>All files are assumed to be tab-separated text files.</b>

| File type | Source | Contents | 
| --------- | ------ | -------- | 
| Data file | SoftMaxPro v5.4.5 | Raw data from plate reader
| Layout file | layout_template.xltx | Location of samples on plate

Plateau is currently only built to parse data files obtained from exporting raw data from SoftMaxPro v5.4.5 on a computer running Windows 7. There is an example of this in the "test_data" folder.

This repo contains an excel template file that I have created to easily generate layout files (layout_template.xltx). Please ensure that the layout file is plain text!

### Outputs
Plateau will instantly generate a graph of cell viability vs. treatment concentration for every condition in your experiment. Here is what the graph of test\_data\_1 looks like:

![graph image](https://github.com/mitchso/plateau/blob/master/images/mpl_graph.png)

In addition, a tab-delimited results file will be written which includes:

* Summary of all experimental information (treatment names, cell line, incubation time, media details, date, etc)
* Analyzed data formatted so that it may be copied directly into GraphPad Prism
* Complete list of all raw data and calculations

### 1 vs 2 plate experiments
Plateau can handle experiments run on one or two plates. If you are running a single plate experiment, plateau calculates cell viability of any given sample based on the control wells contained on the plate.

![sample_viability](http://mathurl.com/yc75ufbh.png)

### Exclude tab
WIP

### Usage example
WIP

## Code overview
WIP
