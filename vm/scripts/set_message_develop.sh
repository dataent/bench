#! /bin/bash

message="
 EPAAS Evaluation VM (built on `date +\"%B %d, %Y\"`)

 Please access EPAAS by going to http://localhost:8000 on the host system.
 The username is \"Administrator\" and password is \"admin\"

 Do consider donating at https://epaas.xyz/buy

 To update, login as
 username: dataent
 password: dataent
 cd dataent-bench
 bench update
"
echo "$message" | sudo tee -a /etc/issue
echo "$message" | sudo tee -a /etc/motd
