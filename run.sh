#!/usr/bin/env bash

# Runs MAVProxy for SITL testing or for the plane.
# ./run.sh -h for help.

BAUDRATE="57600"
DEVICE=""
SITL=false
LEGACY_SITL=false
SITL_LOC=""
SITL_IP=""
AIRAPI_ARG=
OUT_ARG=
# sets the machine variable
UNAMEOUT="$(uname -s)"
case "${UNAMEOUT}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    *)          MACHINE="UNKNOWN:${unameOut}"
esac
echo "Machine is: ${MACHINE}"
HELPTEXT=$'Script for running MAVProxy.

Usage:
    ./run.sh [options]

Options:
    -s \t\t\t run MAVProxy on the SITL (Project Atlas)
    -S \t\t\t run MAVProxy using the legacy sitl
    -l <location> \t if running on SITL, use custom location. See https://github.com/ArduPilot/ardupilot/blob/master/Tools/autotest/locations.txt for list of possible locations
    -f <realflight ip> \t if running on SITL, connect to RealFlight 8 simulator. See http://ardupilot.org/dev/docs/sitl-with-realflight.html for more info.
    -a \t\t\t run MAVProxy in AirAPI mode
    -b <baudrate> \t use inputted baudrate (defaults to 115200)
    -d <device path>\t use inputted serial device (defaults to connected PixHawk)
    -o <gcs ip>\t\t output mavlink packets to external ip (With AirAPI defaults to 192.168.0.35)'

while getopts ":b:d:o:l:f:sShat" opt; do
  case ${opt} in
    a)
      echo "Starting in AirAPI mode"
      AIRAPI_ARG="--airapi"
      ;;
    o)
      echo "Forwarding info to $OPTARG"
      OUT_ARG="--out=udp:$OPTARG:14551"
      ;;
    s)
      echo "Running Project Atlas SITL"
      SITL=true
      echo "$OPTARG"
      ;;
    S)
      echo "Running legacy SITL"
      SITL=true;
      LEGACY_SITL=true
      echo "$OPTARG"
      ;;
    l)
      SITL_LOC=$OPTARG
      ;;
    f)
      SITL_IP=$OPTARG
      ;;
    b)
      BAUDRATE=$OPTARG
      ;;
    d)
      DEVICE=$OPTARG
      ;;
    h)
      echo "$HELPTEXT"
      exit 0
      ;;
    \?)
      echo "Invalid option: -"$OPTARG"" 1>&2
      exit 1;;
    : ) 
      echo "Option -"$OPTARG" requires an argument." >&2
      exit 1;;
  esac
done

# Startup mysql database
docker run -itd --rm --name mysql_container --network=host -v mysql-data:/var/lib/mysql cuairautopilot/private_repo:mysql_image
# docker run -itd --rm --name mysql_container --network=my-network -v mysql-data:/var/lib/mysql cuairautopilot/private_repo:mysql_image
# Look for the device (radio or microusb cable) that a pixhawk might be connected to
if [[ "$DEVICE" == "" ]] ; then
    if [[ "$MACHINE" == "Mac" ]] ; then
      DEVICE=`ls /dev/tty.usb* | tail -n +1 | head -1`
    elif [[ "$MACHINE" == "Linux" ]] ; then
      DEVICE=`ls /dev/serial/by-id/* | grep 'PX4\|FTDI'| head -1`
    else
      echo "No Autodetection of ports for machine: $MACHINE"
    fi
fi

# If AirAPI is active and out_arg is not set manually, set it to 192.168.0.35
if [[ "$AIRAPI_ARG" == "--airapi" ]] ; then
  echo $OUT_ARG
  if [ -z "$OUT_ARG" ] ; then
    echo "Forwarding info to 192.168.0.35"
    OUT_ARG="--out=udp:192.168.0.35:14551"
  fi
else 
  echo $OUT_ARG
  if [ -z "$OUT_ARG" ] ; then # if out_arg has not been set manually
    echo "Forwarding info to docker host"
    OUT_ARG="--out=udp:mavproxy_container:14550"
  fi
fi

if [ "$SITL" = true ] ; then
    if [[ "$SITL_LOC" != "" ]] ; then
        SITL_LOC=" --location $SITL_LOC"
    fi

    if [[ "$SITL_IP" != "" ]] ; then
        SITL_IP=" -f flightaxis:$SITL_IP"
    fi
      
    echo "Stopping Existing SITL dockers"
    docker stop sitl_container > /dev/null

    if [ "$LEGACY_SITL" = true ] ; then
      echo "Starting Legacy SITL docker"
      docker run -itd --rm --name sitl_container --network=host cuairautopilot/private_repo:sitl_image -C $AIRAPI_ARG $OUT_ARG $SITL_LOC
    else
      echo "Starting Project Atlas SITL docker"
      docker run -itd --rm --name sitl_container --network=host cuairautopilot/private_repo:project_atlas_image -C $AIRAPI_ARG $OUT_ARG $SITL_LOC
    fi

    echo "Starting new MAVProxy docker"
    # docker run -it --rm --name mavproxy_container -p 8001:8001 --network=my-network --mount type=bind,source=$PWD,target=/root/mavproxy \
    #   -v node-modules-data:/root/mavproxy/MAVProxy/modules/server/static/node_modules/ cuairautopilot/private_repo:mavproxy_image

    python3 MAVProxy/mavproxy.py --sitl=127.0.0.1:5760 --master=127.0.0.1:14550
else
    # connect to DEVICE at BAUDRATE
    if [[ "$DEVICE" == "" ]] ; then
      echo "No serial input device detected."
      exit 1
    fi
    python MAVProxy/mavproxy.py --master $DEVICE --baudrate $BAUDRATE $AIRAPI_ARG $OUT_ARG
fi


