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

## Steps to run system ##

### 1. Start Evaluation Server locally on Ultra96 ###

Note; Skip to Section 2 if not testing with Evaluation Server

1. Open new terminal and SSH into Sunfire  
`ssh <your NUSNET>@sunfire.comp.nus.edu.sg`  
e.g. `ssh e1234567@sunfire.comp.nus.edu.sg`
2. SSH into Ultra96  
`ssh xilinx@<IP_ADDRESS_OF_ULTRA96>`
3. Deactivate virtual environment if necessary  
`conda deactivate`
4. Go to ultra96_scripts folder  
`cd ultra96_scripts`
5. Run eval_server.py script  
`python3 eval_server.py [IP ADDRESS] [PORT NUMBER] [GROUP ID]`  
e.g. `python3 eval_server.py 127.0.0.1 8888 12`

### 2. Start server on Ultra96 ###

1. Open new terminal and SSH into Sunfire  
`ssh <your NUSNET>@sunfire.comp.nus.edu.sg`  
e.g. `ssh e1234567@sunfire.comp.nus.edu.sg`
2. SSH into Ultra96  
`ssh xilinx@<IP_ADDRESS_OF_ULTRA96>`
3. Deactivate virtual environment if necessary  
`conda deactivate`
4. Go to ultra96_scripts folder  
`cd ultra96_scripts`
5. Open config.py and set the following parameters based on your requirements:  
`IS_EVAL` - set to 1 if connecting to Evalution Server, else 0 (i.e. if skipped previous section, set this to 0)  
`NUM_DANCERS` - set to the number of dancers using this system (1, 2 or 3). `IS_EVAL` needs to be 0 for `NUM_DANCERS` < 3
6. Run main.py  
`sudo python3 main.py`

### 3. Start Laptop script ###

1. Ensure virtual environment is started  
`pipenv shell` (from External_Comms directory)
2. Go to laptop directory  
`cd laptop`
3. Scan for your beetle's mac address by searching for "bluno"  
`bluetoothctl`  
`scan on`
4. Exit bluetoothctl  
`exit`
5. Make change to main.py: **line 17** by replacing with your beetle's mac address. You may have to commment/uncomment mac addresses above line 17 to match your beetle's address  
`vim main.py`
6. Do the same for bluno.py: **line 18**. You may have to commment/uncomment mac addresses above line 18 to match your beetle's address  
`vim bluno.py`
7. Run main.py script with dancerId as parameter  
`python3 main.py [dancerId]`  
e.g. `python3 main.py 1`
