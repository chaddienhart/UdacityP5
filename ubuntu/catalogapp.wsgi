#!/usr/bin/python2
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,'/var/www/CatalogApp/')

from CatalogApp import app as application
application.secret_key = 'Xsw2zaq!'
