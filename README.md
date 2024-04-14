# OmniPkg
OmniPkg is a simple wrapper around your other package managers to allow you to access them all from one place. It has both a GUI and CLI interface available.

# Status
OmniPkg is still in development. It is not itself packaged for any distros and it only supports a few package managers out of the box.

# Features
 - Access basic functions of all your package managers from one application
 - Add new package managers with simple JSON files

# Using It

--- Omnipkg is currently in the middle of a refactor and the instructions below may not work ---

OmniPkg is still in development, currently to use it you will simply:
 - Clone the repo
 - In a terminal navigate to the git repo folder
 - Build the package with "python3 -m build"
 - Navigate to the new "dist" folder
 - Install the .whl file with pip "python3 -m pip install WHEEL_FILENAME_HERE.whl"
    - If you want to be able to use the gui desktop icons you'll need to use "python3 -m pip" not "pip3" so it will install system wide and the binary will be in the expected location
 - To use the GUI app run "omnipkg-gui" in a terminal
    - To install the desktop entry and icons so OmniPkg shows up in your application menu run "omnipkg-gui install-appfiles"
 - To use the CLI app run "omnipkg" in a terminal, get help on the commands with "omnipkg --help"

 # Configuration
 You can add or change the package manager definition JSON files. To do so, add your new pm-def files in the ~/.config/omnipkg/pm-defs directory.

 # Supported package managers
 - Eopkg
 - Flatpak
 - Snap
 - Pacman (untested)

 # TODO
 - Add support for Apt package manager
 - Fix cli install so that if there are multiple results you can select between them (kind of like how Flatpak does it)
 - Make it so cli doesn't use polkit (and thus you just use sudo like you would with any other cli package manager)
 - Polish GUI
 - Add way to clear cache and advanced configuration/settings