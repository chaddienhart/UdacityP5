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
```  git clone https://github.com/chaddienhart/UdacityP5.git```<br>
```  cd ./UdcityP5/ubuntu```<br>
```  sudo chmod 744 step1.sh```<br>
```  sudo ./step1.sh```<br>
Follow the prompts, when done you will have your own version of this project running.
#What the setup scripts are doing
##User setup:
Creates a new user 'grader'

You will need to update your OAuth2 providers. This project uses Google, Facebook, and GitHub.<br>
# Work in progress check back for updates

This repository was created from UdacityP3_ItemCatalog, proj5 branch using:<br>
```  \GitHub\UdacityP3_ItemCatalog [proj5]> git push https://github.com/chaddienhart/UdacityP5.git +proj5:master```

