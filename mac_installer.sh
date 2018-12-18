#!/usr/bin/env bash

#
# This script will (hopefully) install Plateau as a self-contained application on a Mac.
# It must be executed within the github/plateau/ folder.
#

gui_path=`pwd`'/gui.py'
spec_path=`pwd`'/plateau.spec'
ico_path=`pwd`'/plateau.icns'

# note: use spec_path if repeating the command.
pyinstaller --onefile --name plateau --icon $ico_path --windowed --debug=all $gui_path

#   --clean:    Clean PyInstaller cache and remove temporary files before building.
#   --onefoler
#   --onefile
#   --windowed / --noconsole