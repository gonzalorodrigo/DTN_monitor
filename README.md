# DTN_monitor

DTN_only/
* DTN_monitor.ipynb (Jupyter notebook)
* dtnmonitor.py (main entrance for jupyter UI. include download(), because it needs to show current frame)
* bandw.py (monitor graph)
* calldtnscript.py (call dtnscript.sh)
* dtnscript.sh (write dtn information to mongoDB)
* downloadncar.py (download example)
* monitor(CPU, mem, network, IO data generated from bandw.py)
* NOAA/ (download data will be saved here)
  * grib2	(original)

 
Environment Setting
•	Jupyterhub
# Update source
sudo apt-get   update

# Install python-pip python3-pip and ansible
sudo  apt-get  -y  install  python-pip  python3-pip ansible

# Install libzmq3, python and python3 develop packages
sudo  apt-get  -y install  python3-dev  python-dev libzmq3-dev

# Instll require packages for jupyterhub
sudo  apt-get -y  install   npm   nodejs-legacy

# Use npm install http proxy
sudo  npm   install   -g  configurable-http-proxy

# Use pip3 install jupyterhub and notebook
sudo   pip3   install   jupyterhub
sudo   pip3   install   notebook
sudo   pip3   install   paramiko


•	Python library
o	matplotlib: sudo apt-get install python3-matplotlib
o	psutil (for monitor data): sudo pip3 install psutil
o	numpy: sudo pip3 install numpy
•	pymongo
sudo pip3 install pymongo
•	lspci
sudo apt-get install pciutils

 
Usage

1.	Copy folder DTN_only to your home directory
2.	Start Jupyterhub
3.	Open web browser  http://<your IP>:8000/
4.	Sign in 
5.	Execute jupyter notebook step by step

 
 
Author Information: Peggy Lu (peggylu@narlabs.org.tw)

