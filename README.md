# OmniPkg
OmniPkg is a simple wrapper around your other package managers to allow you to access them all from one place. It has both a GUI and CLI interface available.

# Status
OmniPkg is still in development. It is not itself packaged for any distros and it only has a JSON definition file for eopkg currently.

# Features
 - Access basic functions of all your package managers from one application
 - Add new package managers with simple JSON files

# Using It
OmniPkg is still in development, currently to use it you will simply:
 - Clone the repo
 - In a terminal navigate to the git repo folder
 - Build the package with "python3 -m build"
 - Navigate to the new "dist" folder
 - Install the .whl file with pip "pip3 install WHEEL_FILENAME_HERE.whl"
 - To use the GUI app run "omnipkg-gui" in a terminal
 - To use the CLI app run "omnipkg" in a terminal, get help on the commands with "omnipkg --help"

 # Configuration
 You can add or change the package definition JSON files.
 You can find these files in ~/.config/omnipkg/pm-defs after installation.