#!/bin/bash

# RUN THIS ONLY IF DATA DUMP WAS SUCCESSFUL

#~~~~ UESR PARAMS ~~~~~~~~~~~~~~~~~~
USER_START_DATE='yesterday' #  man date (man gdate) to see acceptable arguments 
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

mysql -u root -paeolus mavproxy -e "
	DELETE FROM vfr_hud
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM attitude
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM global_position_int
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM gps_link
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM plane_link
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM battery
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM wind
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM safety
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM mav_message
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM waypoints
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM mode 
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM obstacles
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM current_wp
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM gps_status
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM flight_time
	WHERE time>'$START_DATE' AND time<'$END_DATE';
	DELETE FROM signal_status
	WHERE time>'$START_DATE' AND time<'$END_DATE';
"
