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
python-pip
pip install virtualenv
# system monitoring and maintenance
apachetop
goaccess
fail2ban
nagios3 nagios-nrpe-plugin
nagios-nrpe-server nagios-plugins
unattended-upgrades
```
###Make sure your server has the right time and gets automatic package updates
Setup NTP, Network Time Protocol, by stopping the service forcing the time to update and then restarting. see http://askubuntu.com/questions/254826/how-to-force-a-clock-update-using-ntp
<br>
Setup automatic updates with the unattended-upgrades package see http://askubuntu.com/questions/9/how-do-i-enable-automatic-updates
Turn on security updates with ```sudo dpkg-reconfigure --priority=low unattended-upgrades```<br>
Turn on 50 unattended updates by editing /etc/apt/apt.conf.d/50unattended-upgrades and uncommenting this line (line 4):<br>
```${distro_id} ${distro_codename}-updates";```
###Setup Apache2 to host a Flask web app
Create the following directory sturcture:
```
/var/www/CatalogApp/CatalogApp
/var/www/CatalogApp/CatalogApp/static
/var/www/CatalogApp/CatalogApp/templates
```
Create a vitual environment to keep the application and its dependencies isolated from the main system. I setup the following items used by the web app in the virtual environment.<br>
```
Flask
cloudinary
dict2xml
oauth2client
python-sqlalchemy
```
Configure the virtual host by updating /etc/apache2/sites-available/CatalogApp.conf<br>
Configure the WSGI ```/var/www/CatalogApp/catalogapp.wsgi``` and enable the app with ```sudo a2ensite CatalogApp```<br>
Note: make sure you add ```Options -Indexes``` to the WSGI to disallow directory listing.<br>
Initially we will create a basic /var/www/CatalogApp/CatalogApp/__init__.py to make sure things are working before proceeding.<br>
Restart apache2 and you should see "Hello, I love Digital Ocean!" when browsing to the app now.
<br>reference: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
###Configure the PostgreSQL database
The scripted version will simply recall the PostgreSQL database that was setup originally using:<br>
```
    sudo cp ./ubuntu/mycatalog /var/lib/postgresql
    sudo -u postgres -i
    psql -f mycatalog postgres
    exit
```
Here are the steps taken to setup that database.<br>
####Add and configure role 'catalog', don't forget to set the password
Note: I had trouble connecting to the database until I set the password for 'catalog'
```
sudo -u postgres -i
psql
create role catalog;
alter user catalog with password 'catalog';
GRANT ALL ON SCHEMA public TO catalog;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public to catalog;
\q
```
####Setup the database tables and populate catagories
```
 sudo -u postgres -i
 cd /var/www/CatalogApp/CatalogApp/ubuntu
 python database_setup.py
psql
  \c catalog
  insert into categories (id, name) VALUES (DEFAULT, 'Flowers');
  insert into categories (id, name) VALUES (DEFAULT, 'Fruit');
  insert into categories (id, name) VALUES (DEFAULT, 'Herbs');
  insert into categories (id, name) VALUES (DEFAULT, 'Vegetables');
  \dt
```
You should see the following:<br>
```
        catalog=> \dt
                   List of relations
         Schema |    Name    | Type  |  Owner
        --------+------------+-------+----------
         public | categories | table | postgres
         public | items      | table | postgres
         public | users      | table | postgres
        (3 rows)
```
from linux prompt you should be able to connect to the database with the following:<br>
```psql catalog -h 127.0.0.1 -d catalog```
<br>
If you need to restart your PostgreSQL database: ```sudo /etc/init.d/postgresql restart```<br>
A useful list of Postgres commands: http://postgresonline.com/special_feature.php?sf_name=postgresql83_psql_cheatsheet&outputformat=html
<br>
References:
<br>https://www.digitalocean.com/community/tutorials/how-to-use-roles-and-manage-grant-permissions-in-postgresql-on-a-vps--2
<br>https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04
<br>https://www.digitalocean.com/community/tutorials/how-to-secure-postgresql-on-an-ubuntu-vps
###Set up Fail2ban to protect against attack
Fail2ban will lockout ip addresses that have more than three failed login attemps. Currently the lock out is only 10 minutes but that can be increased by editing /etc/fail2ban/jail.local.<br>
Some setup was needed to switch fail2ban to monitor SSH on port 2200, referenced https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-ubuntu-12-04
###Set up Nagios to monitor server status
I chose Nagios3 to monitor my server because there is a package that installs it and it has the ability to monitor my PostgreSQL database with a built in plugin (only minor configuration needed). Also user 'skh' seemed to have had success using it for this purpose.
Reference:
<br>https://www.howtoforge.com/nagios-on-ubuntu-14.04-trusty-tahr-and-debian-7-wheezy
###Other setup required
You will need to update your OAuth2 providers. This project uses Google, Facebook, and GitHub.<br>
<br>This repository was created from UdacityP3_ItemCatalog, proj5 branch using:<br>
```  \GitHub\UdacityP3_ItemCatalog [proj5]> git push https://github.com/chaddienhart/UdacityP5.git +proj5:master```

