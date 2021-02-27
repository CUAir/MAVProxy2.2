#!/bin/bash
curl -L http://autotest.diydrones.com/Parameters/ArduPlane/apm.pdef.xml > apm.xml
python paramXMLParser.py
cat "apm.js" | tr "'" '"' | sed 's/\([a-zA-Z0-9]\)"\([a-zA-Z0-9]\)/\1\2/g' | sed 's/}, /},\
/g' | sed "s/ArduPlane://g" > "apm2.js"
rm "apm.js"
mv "apm2.js" "../js/utils/ParamDocumentation.js"
rm "apm.xml"