# External Communications #

## Prerequistes ##
1. Python 3.9 installed
2. Pip installed

## Setting up ##

1. Install pipenv on your local system  
`pip install pipenv`
2. Go to External_Comms directory  
`cd External_Comms`
3. Create virtual environment and install dependencies using pipenv  
`pipenv install`
4. Start virtual environment  
`pipenv shell`

## Steps to run Laptop script for Evaluation ##

1. Ensure virtual environment is started  
`pipenv shell` (from External_Comms directory)
2. Go to laptop directory  
`cd laptop`
3. Run main.py script with dancerId as parameter  
`python3 main.py [dancerId]` e.g. `python3 main.py 1`

## Steps for self-testing (Ultra96 with Laptop + Bluno, no Eval Server) ##
### Start server on Ultra96 ###
1. SSH into Sunfire   
(from terminal) `ssh <your NUSNET>@sunfire.comp.nus.edu.sg` e.g. `ssh e1234567@sunfire.comp.nus.edu.sg`
2. SSH into Ultra96  
`ssh xilinx@137.132.86.235`
3. Deactivate virtual environment if necessary  
`conda deactivate`
4. Go to ultra96_scripts folder  
`cd ultra96_scripts`
5. Open config.py and set NUM_DANCERS = 1 (pls change back after done)
6. Run main.py  
`sudo python3 main.py`

### Start Laptop script ###
1. Ensure virtual environment is started  
`pipenv shell` (from External_Comms directory)
2. Go to laptop directory  
`cd laptop`
3. Scan for your beetle's mac address by searching for "bluno" 
`bluetoothctl`
`scan on`
4. Exit bluetoothctl
`exit`
5. Make change to main.py: lines _ and _ by replacing with your beetle's mac address
`vim main.py`
7. Do the same for bluno.py: lines _ and _
`vim bluno.py`
9. Run main.py script with dancerId = 1  
`python3 main.py 1`
