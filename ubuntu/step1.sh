#!/bin/bash
# after following the steps on the developer environment udacity page
# copy the contents of this file to ubuntu vpc
# chmod 744 on the file (step1.sh) to make it executable
# follow the instructions for the second answer:
#     http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none
#     edit /etc/hosts and append your new hostname to the 127.0.0.1 line
# for example: 127.0.0.1 localhost ip-10-20-35-55

# step 1
#make the other scripts executable
sudo chmod 744 step2.sh
sudo chmod 744 FlaskAppSetup.sh

echo "Update ubuntu packages."
sudo apt-get -y update
sudo apt-get -y upgrade

echo
ehco "Add new user 'grader' and set ssh up access"
sudo adduser grader

touch /etc/sudoers.d/grader
echo "# this file was created by chad to grant grader sudo permissions" > /etc/sudoers.d/grader
echo "grader ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/grader

# give ssh to grader using the same key assigned to root
mkdir /home/grader/.ssh
cp ~/.ssh/* /home/grader/.ssh
chown grader /home/grader/.ssh -R

echo
echo "Switching to using port 2200, and locking out 'root'"
#make a backup just in case something goes wrong...
sudo cp /etc/ssh/sshd_config /etc/ssh/original_sshd_config
sudo cp ./sshd_config /etc/ssh/sshd_config
sudo service ssh restart

echo "ssh port set to 2200, and root has been locked out
verify you can login as grader or chad and that you have
sudo power before closing this session.
open a new shell and connect with:
ssh -i ~/.ssh/udacity_key.rsa grader@52.26.180.232 -p 2200

then run step2.sh from the new 'grader' shell and close this one"
