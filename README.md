### Udacity Full Stack Web Developer
# Project 5 - Linux server configuration
This project details setting up a web app using Linux, Apache2, PostgreSQL, and Flask<br>
You can see this web app running at http://54.183.181.211/catalog/ on an EC2 Ubuntu instance.<br>
See: https://github.com/chaddienhart/UdacityP3_ItemCatalog/blob/master/README.md <br>
  for details on the contents of the web app itself.
#Getting started
Although it was not required in this project I have written scripts to preform the major tasks of configuing my Linux server. So to use this repository to setup a server, get your Ubuntu 14.04 server running and log in as 'root' using ssh and your private key<br>
First to get this repository you will need to install git<br>
```  sudo apt-get install git-all ```<br>
```  sudo apt-get install git ``` (EC2)<br>
Then clone the repository and run step1.sh<br>
```
cd /
sudo git clone https://github.com/chaddienhart/UdacityP5.git
cd ./UdcityP5/ubuntu
sudo chmod 744 step1.sh
sudo ./step1.sh
```
At the Package configuration prompt, select "keep the local version currently installed"<br>
Follow the prompts, when done you will have your own version of this project running.<br>
When asked for a password for grader you can simply enter blank as passwords will be disable.<br>
After the scripts have completed you will need to update the IP address in /etc/apache2/sites-available/CatalogApp.conf and update the PostgreSQL database (steps at the end of step2.sh)<br>
```
sudo cp mycatalog /var/lib/postgresql/
sudo -u postgres -i
psql -f mycatalog postgres
exit
sudo service apache2 restart
```
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
Setup automatic updates with the unattended-upgrades package see<br> http://askubuntu.com/questions/9/how-do-i-enable-automatic-updates <br>
Turn on security updates with ```sudo dpkg-reconfigure --priority=low unattended-upgrades```<br>
Turn on 50 unattended updates by editing ```/etc/apt/apt.conf.d/50unattended-upgrades``` and uncommenting this line:<br>
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
Configure the virtual host by updating ```/etc/apache2/sites-available/CatalogApp.conf```<br>
Configure the WSGI ```/var/www/CatalogApp/catalogapp.wsgi``` and enable the app with ```sudo a2ensite CatalogApp```<br>
Note: make sure you add ```Options -Indexes``` to the WSGI to disallow directory listing.<br>
Initially we will create a basic ```/var/www/CatalogApp/CatalogApp/__init__.py``` <br>
Test to make sure things are working before proceeding.<br>
Restart apache2 (```sudo service apache2 restart```) and you should see "Hello, I love Digital Ocean!" when browsing to the app now.
<br>reference: https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
###Configure the PostgreSQL database
The scripted version will simply recall the PostgreSQL database that was setup originally using:<br>
```
    sudo cp ./ubuntu/mycatalog /var/lib/postgresql
    sudo -u postgres -i
    psql -f mycatalog postgres
    exit
```
#####Here are the steps taken to setup that database.<br>
Add and configure role 'catalog', don't forget to set the password<br>
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
Setup the database tables and populate catagories
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
Fail2ban will lockout ip addresses that have more than three failed login attemps. Currently the lock out is only 10 minutes but that can be increased by editing ```/etc/fail2ban/jail.local```<br>
Some setup was needed to switch fail2ban to monitor SSH on port 2200, I followed the steps referenced here:<br> https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-ubuntu-12-04
###Set up Nagios to monitor server status
I chose Nagios3 to monitor my server because there is a package that installs it and it has the ability to monitor my PostgreSQL database with a built in plugin (only minor configuration needed). Also user 'skh' seemed to have had success using it for this purpose.<br>
You can access Nagios monitoring at: http://52.32.84.113/nagios3/ <br>
Username: ```nagiosadmin```<br>
Password: ```udacity2Grade```<br>
To get nagios3 configured to run, modify the user to be in www-data group and make it executable:<br>
```
sudo usermod -a -G nagios www-data
sudo chmod -R +x /var/lib/nagios3/    
```
In /etc/nagios3/nagios.cfg set ```check_external_commands=1```<br>
Now you can login to http://your_site/nagios3 using the nagiosadmin user and password you set. Notice the SSH server will not be responding because we need to reconfigure nagios to monitor SSH on port 2200. Configure this by editing /etc/nagios3/conf.d/services_nagios2.cfg, find the ssh-servers service definition and change it to:<br>
```
    # check that ssh services are running
    define service {
            hostgroup_name                  ssh-servers
            service_description             SSH
            check_command                   check_ssh_port!2200
```
To setup PostgreSQL monitoring, add the following to /etc/nagios-plugins/config/pgsql.cfg<br>
```
    define command{
            command_name    check_pgsql_cat
            command_line    /usr/lib/nagios/plugins/check_pgsql -d catalog -H 127.0.0.1 -l 'catalog' -p 'catalog'
```
Add the following to /etc/nagios3/conf.d/postgre_nagios2.cfg (note you will have to create this file)<br>
```
    define service{
            hostgroup_name                  postgresql-servers
            service_description             check_pgsql
            check_command                   check_pgsql_cat
            use                             generic-service
    }
```
Finally add the following to /etc/nagios3/conf.d/hostgroups_nagios2.cfg<br>
```
define hostgroup {
        hostgroup_name postgresql-servers
                members         localhost
        }
```
Restart nagios<br>
```
sudo service nagios-nrpe-server restart            
sudo service nagios3 restart
```
You should now see all seven services running with a status of 'OK' under http://your_site/nagios3/ and click the 'Host groups' link on the left panel and then click on one of the 'localhost' links.<br>
To see it working try stopping the PosgreSQL server, ```sudo /etc/init.d/postgresql stop``` and wait a couple of minutes and nagios will report the 'check_pgsql' service as 'CRITICAL'. Correct this problem by restarting PostgreSQL ```sudo /etc/init.d/postgresql start```
References:
<br>https://www.howtoforge.com/nagios-on-ubuntu-14.04-trusty-tahr-and-debian-7-wheezy
<br>https://viewsby.wordpress.com/2012/07/10/nagios-change-ssh-port/
###Other setup required
I had to change a few of the SQLalchemy calls to group_by, just returning all is acceptable for my database because the categories are not user configurable so there should not be duplicates. See https://discussions.udacity.com/t/sqlalchemy-error-using-postgresql-works-under-sqlite/33200 <br>
I encountered a problem with the count() in the templates/catalog.html
and had to change ```{% for c in range(0, categories.count()) %}``` to ```{% for c in categories %}``` <br>
I had to fully specify the client secret files used for OAuth2. <br>
You will need to update your OAuth2 providers. This project uses Google, Facebook, and GitHub.<br>
<br>This repository was created from UdacityP3_ItemCatalog, proj5 branch using:<br>
```  \GitHub\UdacityP3_ItemCatalog [proj5]> git push https://github.com/chaddienhart/UdacityP5.git +proj5:master```

