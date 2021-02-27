#!/bin/sh
if [ -d 'venv' ]; then
  exit 0
fi
pip install virtualenv
virtualenv venv
source venv/bin/activate
pip install selenium
brew install chromedriver