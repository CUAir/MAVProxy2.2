#!/bin/bash

#~~~~ UESR PARAMS ~~~~~~~~~~~~~~~~~~
FILENAME="data/2017-02-25:2017-03-25.sql"  #.i.e. data/2017-10-5:2017-10-6.sql
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

mysql -u cuair -paeolus mavproxy < $FILENAME
