#!/bin/bash
# copy the contents of this file to ubuntu vpc
# chmod 744 on the file to make it executable
curDir=$(pwd)
echo "setting up a flask app in /var/www"
cd /var/www
sudo mkdir CatalogApp
cd CatalogApp
sudo mkdir CatalogApp
cd CatalogApp
sudo mkdir static templates
sudo pip install virtualenv
sudo virtualenv venv
source venv/bin/activate 
sudo pip install Flask
sudo pip install cloudinary
sudo pip install dict2xml
sudo pip install oauth2client
sudo apt-get install -y python-sqlalchemy
deactivate

cd $curDir
echo
echo "the current directory is $curDir"
sudo cp ./__init__step1.py /var/www/CatalogApp/CatalogApp/__init__.py
sudo cp ./CatalogApp.conf /etc/apache2/sites-available/CatalogApp.conf

#Now enable it:
sudo a2ensite CatalogApp

#Setup the wsgi file:
sudo cp ./catalogapp.wsgi /var/www/CatalogApp/catalogapp.wsgi
#restart apache2
sudo service apache2 restart 

#these files and steps are from
# https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
echo
echo "******************************************"
echo "You will need to edit /etc/apache2/sites-available/CatalogApp.conf
and update the server address."
echo "restart apache2 when you are done."
echo "Reload the web page and you should now see 
    - Hello, I love Digital Ocean! -"
read


