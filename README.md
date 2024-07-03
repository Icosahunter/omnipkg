# OmniPkg
OmniPkg is a simple wrapper around your other package managers to allow you to access them all from one place. It has both a GUI and CLI interface available.

# Status
OmniPkg is still in development. It is not itself packaged for any distros and it only supports a few package managers out of the box.

# Features
 - Access basic functions of all your package managers from one application
 - Add new package managers with simple config files (default is TOML but Omnipkg should recognize JSON and INI files as well)

# Using It

OmniPkg is still in development and not ready for normal use.

If you want to run Omnipkg for testing without installing:
 - Clone the repo
 - In a terminal navigate to the git repo folder
 - If you have Just simply do "just gui" (or "just cli" for the command line interface, this just command can't take flags however)
   - This Just command creates a venv, installs the dependencies, and runs the code as a module from the src directory.
 - If you do not have Just:
   - Install the dependencies in "requirements.txt" (in a virtual environment or otherwise)
   - Do "cd src"
   - Do "python3 -m omnipkg.gui" (or "python3 -m omnipkg.cli" with arguments for the command line interface)

Installing Omnipkg:
 - Clone the repo
 - In a terminal navigate to the git repo folder
 - If you have Just installed, you can install it with simply "just install"
 - If you do not have Just installed:
   - Build the package with "python3 -m build"
   - Navigate to the new "dist" folder
   - Install the .whl file with pip "python3 -m pip install WHEEL_FILENAME_HERE.whl"
 - To use the GUI app run "omnipkg-gui" in a terminal
    - To install the desktop entry and icons so OmniPkg shows up in your application menu run "omnipkg-gui install-appfiles"
 - To use the CLI app run "omnipkg" in a terminal, get help on the commands with "omnipkg --help"

 # Configuration

 ## Package Manager Definitions
 You can add or change the package manager definition JSON files. To do so, add your new pm-def files in the ~/.config/omnipkg/pm-defs directory.
 Take a look at the existing pm-def files in this repository to understand the format. This format is likely to change as it is a bit terse currently.

 ## Package Details Formatting
 You can change the way the package details are shown in the right pane by placing a markdown file named "package-details-template.md" in the
 ~/.config/omnipkg/ directory, using python formatting syntax for values to insert. See the default template in this repository for an example.
 Valid package attributes for the template are:
 - name
 - id
 - pm
 - summary
 - description
 - website
 - icon_url
 - icon
 - installed
 - updatable

 # Supported package managers
 - Eopkg
 - Flatpak
 - Snap
 - Pacman (untested, this will likely require some new features for detecting user input prompts)

 # TODO
 - Add support for Apt package manager
 - Polish GUI
 - Add advanced configuration/settings