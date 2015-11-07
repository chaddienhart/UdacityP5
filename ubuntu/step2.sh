#!/bin/bash
# make this file executable
# chmod 744 on the file to make it executable
echo "setting up the firewall"
sudo ufw status
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 2200/tcp
sudo ufw allow www
sudo ufw allow ntp
sudo ufw enable
sudo ufw status verbose
echo "firewall setup complete"
echo
echo "hit enter to continue"
read
echo "install needed packages"
sudo apt-get install -y apache2
sudo apt-get install -y python
sudo apt-get install -y libapache2-mod-wsgi
sudo apt-get install -y postgresql postgresql-contrib
sudo apt-get install -y libapache2-mod-wsgi python-dev
sudo apt-get install -y python-psycopg2
sudo apt-get install -y libpq-dev
sudo apt-get install -y ntp
sudo apt-get install -y python-pip
sudo pip install virtualenv
# system monitoring and maintenance
sudo apt-get install -y unattended-upgrades
sudo apt-get install -y apachetop
sudo apt-get install -y goaccess
sudo apt-get install -y fail2ban
sudo apt-get install -y nagios3 nagios-nrpe-plugin
sudo apt-get install -y nagios-nrpe-server nagios-plugins

echo "done installing packages, YEAH!"
echo
echo "test that apache2 is up and running, enter the address
from the udacity development environment page.
You should see 'Apache2 Ubuntu Default Page'"
echo
echo "hit enter to continue"
read

echo
echo "make sure time is correct and ntp is running"
sudo service ntp stop
sudo ntpd -gq
sudo service ntp start

echo
echo "turning on unattended-upgrades for security updates"
sudo dpkg-reconfigure --priority=low unattended-upgrades

echo
echo "turn on automatic updates"
sudo cp ./50unattended-upgrades /etc/apt/apt.conf.d/50unattended-upgrades
#sudo gedit /etc/apt/apt.conf.d/50unattended-upgrades
# uncomment this line: 
#        "${distro_id} ${distro_codename}-updates";

echo
echo "Setup fail2ban to protect against repeated failed attempts to log in."
#https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-ubuntu-12-04
#sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
#    add your ip address to ignoreip = 
#    update destemail = 
#    update the ssh port in the iptables
#    port = 2200 
sudo cp ./jail.local /etc/fail2ban/jail.local
sudo service fail2ban restart

echo"Next run FlaskAppSetup.sh"
sh ./FlaskAppSetup.sh

# copy over the source from this repository
echo "Copy the web app from this repository to the Flask application location."
sudo cp -r ../* /var/www/CatalogApp/CatalogApp/
echo

# setup Nagios site monitoring
echo "Setup Nagios to monitor the site and database."
sh ./NagiosSetup.sh
echo
echo
echo "
Setup of the PostgreSQL database is not fully scripted yet. 
You can load the database from this repository as follows:
    sudo cp ./ubuntu/mycatalog /var/lib/postgresql
    sudo -u postgres -i
    psql -f mycatalog postgres
    exit
restart apache2 and reload the page.
    sudo service apache2 restart 
You should now see the Item Catalog app.
"



