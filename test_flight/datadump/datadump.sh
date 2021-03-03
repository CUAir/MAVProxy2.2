#!/bin/bash

#~~~~ UESR PARAMS ~~~~~~~~~~~~~~~~~~
# EDIT THESE!
USER_START_DATE='yesterday'  #  man date (man gdate) to see acceptable arguments 
USER_END_DATE='today'
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



unamestr=`uname`
if [[ "$unamestr" == 'Darwin' ]]; then  # Setup for OSX
    
	# install gdate
	brew ls --versions coreutils > /dev/null
    if [ $? -ne 0 ]; then
  		# The package is installed
  		brew install coreutils
	fi

	START_DATE=$(gdate --date="$USER_START_DATE" "+%Y-%m-%d")
	END_DATE=$(gdate --date="$USER_END_DATE" "+%Y-%m-%d")

elif [[ "$unamestr" == 'Linux' ]]; then  # Setup for Linux
	START_DATE=$(date --date="$USER_START_DATE" "+%Y-%m-%d")
	END_DATE=$(date --date="$USER_END_DsATE" "+%Y-%m-%d")

else
  echo "Error: Unknown OS"
  exit 1
fi

FILENAME="$START_DATE:$END_DATE.sql"


mysqldump -u cuair -paeolus --where="time>='$START_DATE' and time<='$END_DATE'" mavproxy > "data/$FILENAME"
