
# WELCOME!
## Setting Up the python virtual environment
In order to run the cocotb software, one must first configure the appropriate python virtual environment (venv). 

### Windows:
1. Pre-requisite: Ensure that python3.9 is installed
2. Open a command window at the same directory level as this README
3. Run `py -3.9 -m venv venv_cocotb`
4. Run `venv_cocotb\Scripts\activate.bat`. Ensure that the environment correctly activates in the terminal, with "(venv_cocotb)" to the left of the command cursor
5. Run `python -m pip install --upgrade pip` to upgrade to the latest pip
6. Run `python -m pip install -r requirements.txt` to install all requirements
7. The venv is now active. To exit, either close the terminal or run `deactivate`. To re-activate, run `venv_cocotb\Scripts\activate.bat` from the directory of this README.

### Unix(Linux) / MacOS:
1. Pre-requisite: Ensure that python3.9 is installed from the official python.org (it does _not_ have to be configured as the system default python distribution)
2. Open a command window at the same directory level as this README
3. Run `python3 -m venv venv_cocotb`
4. Run `source venv_cocotb/bin/activate`. Ensure that the environment correctly activates in the terminal, with "(venv_cocotb)" to the left of the command cursor
5. Run `python -m pip install --upgrade pip` to upgrade to the latest pip
6. Run `python -m pip install -r requirements.txt` to install all requirements
7. The venv is now active. To exit, either close the terminal or run `deactivate`. To re-activate, run `source venv_cocotb/bin/activate` from the directory of this README.


## Setting up ghdl
- If on Windows, install executable from here: http://ghdl.free.fr/download.html
- If on Mac (with homebrew installed), run `brew install ghdl`
- If on Debian/Ubuntu, run `sudo apt-get install ghdl`
- If on Fedora/CentOS, run `sudo yum install ghdl`
- If on Arch Linux, run `sudo pacman -S ghdl`
* Run `ghdl --version` to verify successfull installation


## GTKWave install instructions
Follow this link for instructions on installing GTKWave https://gtkwave.sourceforge.net


# Running tests
With the virtual environment active and Questa installed with a license setup, one can now run the software.
1. Open a terminal in cocotb-demo
2. Run `python cocotb_runner.py`.
3. When prompted with test groups, enter the corresponding number to the desired test group to run
4. When prompted with tests, enter the corresponding number for the desired test to run, or enter `a` to run all tests

NOTE: Waveforms can be viewed via GTKWave after a completed test run (Does not need to pass)