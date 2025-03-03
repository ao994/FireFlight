# FireFlight
FireFlight capstone 2024-25 project.

# Local hosting instructions
## Prerequisites
1. Make sure you have python installed on your computer. (Instructions for installing found [here](https://wiki.python.org/moin/BeginnersGuide/Download).)
2. Make sure you have mySQL installed and set up on your computer. (Instructions for installing found [here](https://dev.mysql.com/doc/mysql-installation-excerpt/5.7/en/installing.html).)

## Instructions
1. Download this repository onto your computer.
2. Create the missing files: "blank" and "blank"
3. In the FireFlight folder (the main folder) using the terminal/PowerShell/command line, create a Python Virtual Environment (venv) folder named .venv.
    1. Complete instructions found [here](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/).
    2. For Windows: In the FireFlight folder, run this command in PowerShell (in the FireFlight folder!): `python -m venv .venv`
    3. For Mac and Linux: In the FireFlight folder, run this command in your terminal (in the FireFlight folder!): `python3 -m venv .venv`
4. For Windows systems only!: Run the following command to be able to properly install the packages in later steps: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`. This will make it so that the execution policy for scripts executed on your machine allows remotely signed scripts to be executed (which is not allowed by default). For more information on Windows execution policies, read [here](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-executionpolicy?view=powershell-7.5).
5. Run the following command in the terminal from the FireFlight folder to activate the virtual environment (venv): 
    - Windows: `.venv\Scripts\Activate`
    - Mac/Linux: `source .venv/bin/activate`
6. To deactivate the virtual environment (venv) at any point, run this command: `deactivate`.
