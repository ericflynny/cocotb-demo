# THIS PROJECT IS CURRENTLY A WORK IN PROGRESS. The cocotb/ghdl functionality has not been implemented


## Setting Up the Python Virtual Environment
In order to run the cocotb software, one must first configure the appropriate python virtual environment (venv). 

### Windows:
1. Pre-requisite: Ensure that python3.9 is installed
2. Open a command window at the same directory level as this README
3. Run `py -3.9 -m venv venv_cocotb`
4. Run `venv_cocotb\Scripts\activate.bat`. Ensure that the environment correctly activates in the terminal, with "(venv_cocotb)" to the left of the command cursor
5. Run `python -m pip install --upgrade pip` to upgrade to the latest pip
6. Run `python -m pip install -r requirements.txt` to install all requirements
7. The venv is now active. To exit, either close the terminal or run `deactivate`. To re-activate, run `venv_cocotb\Scripts\activate.bat` from the directory of this README.

### Unix(Linux):
1. Pre-requisite: Ensure that python3.9 is installed from the official python.org (it does _not_ have to be configured as the system default python distribution)
2. Open a command window at the same directory level as this README
3. Run `python3.9 -m venv venv_cocotb`
4. Run `source venv_cocotb/bin/activate`. Ensure that the environment correctly activates in the terminal, with "(venv_cocotb)" to the left of the command cursor
5. Run `python -m pip install --upgrade pip` to upgrade to the latest pip
6. Run `python -m pip install -r requirements.txt` to install all requirements
7. The venv is now active. To exit, either close the terminal or run `deactivate`. To re-activate, run `source venv_cocotb/bin/activate` from the directory of this README.


## Running tests
With the virtual environment active and Questa installed with a license setup, one can now run the software.
1. Open a terminal in cocotb-demo
2. Run `python cocotb_runner.py`.
3. When prompted with test groups, enter the corresponding number to the desired test group to run
4. When prompted with tests, enter the corresponding number for the desired test to run, or enter `a` to run all tests