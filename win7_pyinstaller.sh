#!/usr/bin/env bash

#
# This script packages plateau as a standalone windows 7 application.
# Although this works on my computer it is likely that it will not
# work exactly the same for someone else.
# It must be executed within the github/plateau/ folder.
#

gui_path=`pwd`'/gui.py'
ico_path=`pwd`'/plateau.ico'

pyinstaller --name plateau \
            --icon $ico_path \
            --onefile \
            --windowed \
            --add-data "./plateau.png;plateau.png" \
            $gui_path
