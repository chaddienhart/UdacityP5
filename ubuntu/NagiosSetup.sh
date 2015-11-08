#!/bin/bash
# Nagios setup
# steps from https://www.howtoforge.com/nagios-on-ubuntu-14.04-trusty-tahr-and-debian-7-wheezy
sudo usermod -a -G nagios www-data
sudo chmod -R +x /var/lib/nagios3/    
sudo cp ./nagios.cfg /etc/nagios3/nagios.cfg
sudo service nagios3 restart
echo
echo "login to the web site http://<your host>/nagios3"

# need to fix the port to be 2200 (default is 22)
# https://viewsby.wordpress.com/2012/07/10/nagios-change-ssh-port/
# change the ssh port to 2200:
# edit /etc/nagios3/conf.d/services_nagios2.cfg
# change to -
    # check that ssh services are running
#    define service {
#            hostgroup_name                  ssh-servers
#            service_description             SSH
#            check_command                   check_ssh_port!2200
sudo cp ./services_nagios2.cfg /etc/nagios3/conf.d/services_nagios2.cfg

# setup nagios to monitor postgres
# https://www.howtoforge.com/nagios-on-ubuntu-14.04-trusty-tahr-and-debian-7-wheezy
# edit /etc/nagios-plugins/config/pgsql.cfg
# add the following:
#    define command{
#            command_name    check_pgsql_cat
#            command_line    /usr/lib/nagios/plugins/check_pgsql -d catalog -H 127.0.0.1 -l 'catalog' -p 'catalog'
#            }
sudo cp ./pgsql.cfg /etc/nagios-plugins/config/pgsql.cfg

# edit /etc/nagios3/conf.d/ 
# add a file postgre_nagios2.cfg
#   define service{
#            hostgroup_name                  postgresql-servers
#            service_description             check_pgsql
#            check_command                   check_pgsql_cat
#            use                             generic-service
#    }
sudo cp ./postgre_nagios2.cfg /etc/nagios3/conf.d/postgre_nagios2.cfg

# edit /etc/nagios3/conf.d/hostgroups_nagios2.cfg
# add the following:
# define hostgroup {
#        hostgroup_name postgresql-servers
#                members         localhost
#        }
sudo cp ./hostgroups_nagios2.cfg /etc/nagios3/conf.d/hostgroups_nagios2.cfg

# restart nagios
sudo service nagios-nrpe-server restart            
sudo service nagios3 restart
