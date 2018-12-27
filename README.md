<h6 align="center">source code for:</h6>

![plateau](https://github.com/mitchso/plateau/tree/master/images/plateau.png)

<h6 align="center"> open-source, cross-platform, standalone <br> application for microplate data analysis</h6>

## plateau
- [Introduction](#introduction)
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

## Introduction
This is the source code for an application I developed called plateau. It is a pretty straightforward application that is meant to automate the analysis of microplate data from cell-based assays.

As of this moment it can only do one type of analysis and has also only been written with one type of readout file in mind, so there is a pretty good chance this application would have to be adapted if someone else were to use it. 

That being said, feel free to open an issue or submit a pull request if you are interested in using the application and the current version does not suit your needs.

Here's the current look of the application as seen on a Mac:

![Main tab](https://github.com/mitchso/plateau/tree/master/images/main_tab.png)

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
Plateau takes 1-2 pairs of data & layout files. All files are assumed to be tab-separated text files.

| File type | Source | Contents | 
| --------- | ------ | -------- | 
| Data file | SoftMaxPro v5.4.5 | Raw data from plate reader
| Layout file | layout_template.xltx | Location of samples on plate

Plateau is currently only built to parse data files obtained from exporting raw data from SoftMaxPro v5.4.5

This repo contains an excel template file that I have created to easily generate layout files (layout_template.xltx). Please ensure that the layout file is plain text!

### Outputs


### 1 vs 2 plate experiments

### Exclude tab
WIP

### Usage example
WIP

## Code overview
WIP
