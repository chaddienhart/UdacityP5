#!/bin/bash
# copy the contents of this file to ubuntu vpc
# chmod 744 on the file to make it executable
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
deactivate

echo "
cd /var/www/CatalogApp/CatalogApp
sudo touch __init__.py

edit __init__.py and paste the following in:

from flask import Flask
app = Flask(__name__)
@app.route('/')
def hello():
    return 'Hello, I love Digital Ocean!'
if __name__ == '__main__':
    app.run()
    
save and close the file."
echo"
Next configure it:
sudo nano /etc/apache2/sites-available/CatalogApp.conf

paste the following in:

<VirtualHost *:80>
		ServerName 52.26.180.232
		ServerAdmin chaddienhart@gmail.com
		WSGIScriptAlias / /var/www/CatalogApp/catalogapp.wsgi
		<Directory /var/www/CatalogApp/CatalogApp/>
            Options -Indexes
			Order allow,deny
			Allow from all
		</Directory>
		Alias /static /var/www/CatalogApp/CatalogApp/static
		<Directory /var/www/CatalogApp/CatalogApp/static/>
            Options -Indexes			
            Order allow,deny
			Allow from all
		</Directory>
		ErrorLog ${APACHE_LOG_DIR}/error.log
		LogLevel warn
		CustomLog ${APACHE_LOG_DIR}/access.log combined
</VirtualHost>
"

echo "
Now enable it:

sudo a2ensite CatalogApp"

echo "Setup the wsgi file:
cd /var/www/CatalogApp
sudo nano catalogapp.wsgi


#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/CatalogApp/')

from CatalogApp import app as application
application.secret_key = 'Add your secret key'

save and restart apache

sudo service apache2 restart 
"


