#!/usr/bin/env bash

#
# This script packages plateau as a standalone mac application.
# Although this works on my computer it is likely that it will not
# work exactly the same for someone else.
# It must be executed within the github/plateau/ folder.
#

gui_path=`pwd`'/gui.py'
spec_path=`pwd`'/plateau.spec'
ico_path=`pwd`'/plateau.icns'

# note: use spec_path if repeating the command.
pyinstaller --name plateau \
            --icon $ico_path \
            --onefile \
            --windowed \
            --add-binary /Library/Frameworks/Python.framework/Versions/3.7/lib/libtk8.6.dylib:tk \
            --add-binary /Library/Frameworks/Python.framework/Versions/3.7/lib/libtcl8.6.dylib:tcl \
            --add-data /Users/mitchsyberg-olsen/github/plateau/plateau.png:plateau.png \
            $gui_path

