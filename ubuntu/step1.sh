#!/bin/bash
# after following the steps on the developer environment udacity page
# copy the contents of this file to ubuntu vpc
# chmod 744 on the file (step1.sh) to make it executable
# follow the instructions for the second answer:
#     http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none
#     edit /etc/hosts and append your new hostname to the 127.0.0.1 line
# for example: 127.0.0.1 localhost ip-10-20-35-55

sudo apt-get -y update
sudo apt-get -y upgrade
sudo adduser grader
sudo adduser chad

touch /etc/sudoers.d/grader
echo "# this file was created by chad to grant grader sudo permissions" > /etc/sudoers.d/grader
echo "grader ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/grader

touch /etc/sudoers.d/chad
echo "# this file was created by chad to grant chad sudo permissions" > /etc/sudoers.d/chad
echo "chad ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/chad

# give ssh to grader using the same key assigned to root
mkdir /home/grader/.ssh
cp ~/.ssh/* /home/grader/.ssh
chown grader /home/grader/.ssh -R

mkdir /home/chad/.ssh
cp ~/.ssh/* /home/chad/.ssh
chown chad /home/chad/.ssh -R

sudo cp ./sshd_config /etc/ssh/sshd_config
sudo service ssh restart

echo "ssh port set to 2200, and root has been locked out
verify you can login as grader or chad and that you have
sudo power before closing this session.
open a new shell and connect with:
ssh -i ~/.ssh/udacity_key.rsa chad@52.26.180.232 -p 2200
ssh -i ~/.ssh/udacity_key.rsa grader@52.26.180.232 -p 2200"
