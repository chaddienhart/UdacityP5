### Udacity Full Stack Web Developer
# Project 5 - Linux server configuration
This project details setting up a web app using Linux, Apache2, PostgreSQL, and Flask<br>
You can see this web app running at http://52.26.180.232/catalog/<br>
This work was done on a Ubuntu server started by Udacity (actually a EC2 Ubuntu instance).<br>
See: https://github.com/chaddienhart/UdacityP3_ItemCatalog/blob/master/README.md <br>
  for details on the contents of the web app
#Getting started
Although it was not required in this project I have written scripts to preform the major tasks of configuing my Linux server. So to use this repository to setup a server, get your Ubuntu 14.04 server running and log in as 'root' using ssh and your private key<br>
To bring down this source you need to first install git<br>
```  sudo apt-get install -y git-all ```<br>
Bring down the repository and run step1.sh<br>
```
git clone https://github.com/chaddienhart/UdacityP5.git
cd ./UdcityP5/ubuntu
sudo chmod 744 step1.sh
sudo ./step1.sh
```
Follow the prompts, when done you will have your own version of this project running.
##What the setup scripts are doing
###Update the server
The first thing to do when bringing up a Ubuntu server is to update packages. This is done by issuing the following two commands:<br>
```
sudo apt-get -y update
sudo apt-get -y upgrade
```
###User setup:
Creates a new user 'grader', adds the user to allowed sudoers, and copies the public key used by 'root' for use by 'grader'. Methods shown in class.<br>
The SSH port is changed to be 2200 (default is 22) and the user 'root' is locked out by modifying the ```sshd_config``` file. Once this is done you will be prompted to log in on port 2200 and verify that 'grader' has sudo access (test by trying to use sudo). After verifying 'grader' is setup correctly you should exit your 'root' session.
###Firewall configuration:
Lock out everthing then turn on only what we need.<br>
```
sudo ufw status
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow ntp
sudo ufw enable
```
###Install needed packages
Using apt-get and pip install the software needed for our LAMP stack.<br>
```
apache2
python
libapache2-mod-wsgi
postgresql postgresql-contrib
libapache2-mod-wsgi python-dev
python-psycopg2
libpq-dev
ntp
python-sqlalchemy
python-pip
pip install virtualenv
pip install Flask 
# system monitoring and maintenance
apachetop
goaccess
fail2ban
nagios3 nagios-nrpe-plugin
nagios-nrpe-server nagios-plugins
unattended-upgrades
```
###Make sure your server has the right time and gets updated
Setup NTP, Network Time Protocol, by stopping the service forcing the time to update and then restarting. see http://askubuntu.com/questions/254826/how-to-force-a-clock-update-using-ntp
<br>
Setup automatic updates with the unattended-upgrades package see http://askubuntu.com/questions/9/how-do-i-enable-automatic-updates
###Other setup required
You will need to update your OAuth2 providers. This project uses Google, Facebook, and GitHub.<br>
# Work in progress check back for updates

This repository was created from UdacityP3_ItemCatalog, proj5 branch using:<br>
```  \GitHub\UdacityP3_ItemCatalog [proj5]> git push https://github.com/chaddienhart/UdacityP5.git +proj5:master```

