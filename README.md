<p align="center">
<h6 align="center">source code for:</h6>
<h1 align="center">plateau</h1>
<h6 align="center"> open-source, cross-platform, standalone <br> application for microplate data analysis</h6>
</p>
<br>

## Table of contents
- [Introduction](#introduction)
- [Installation](#installation)
    - [Mac](#mac)
    - [Windows](#windows)
- [Usage](#usage)


## Introduction
This is the source code for an application I developed called plateau. It is a pretty straightforward application that is meant to automate the analysis of microplate data from cell-based assays.

As of this moment it can only do one type of analysis and has also only been written with one type of readout file in mind, so there is a pretty good chance this application would have to be adapted if someone else were to use it. That being said, feel free to open an issue or submit a pull request if you are interested in using the application and the current version does not suit your needs.

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
In brief, the tkinter/tcl modules are not properly packaged and will not be found by the application when it is executed on your local computer.

The workaround for this is to install Python 3.7.1 directly from:

```
https://www.python.org/downloads/release/python-371/
```
If you have done this, you should have the correct version of tkinter/tcl visible to the application and it should run without problems. This worked for me when deploying the application onto a different mac, but it is definitely not 
