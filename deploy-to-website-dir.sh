#!/bin/bash

PROJ="/home/jon/proj/efj/toolkit"
WEBSITE="/home/jon/proj/website/content"


echo Activating venv
cd $PROJ
. venv/bin/activate

echo Building documentation
cd $PROJ/docs
make html

echo Building efj.py and efjgui.pyw
cd ..
./make_shiv.sh

echo Copying files
cp efj.py ~/bin/efj  # local
cp efj.py efjgui.pyw ${WEBSITE}/shiv/  # shivs
cp -av ${PROJ}/web-interface/* ${WEBSITE}/efj  # web interface
cp -av ${PROJ}/docs/_build/html/* ${WEBSITE}/efjtkdocs/  # documentation

echo Building website
cd $WEBSITE
ssg

echo Deploying to staging
../deploy

echo Cleaning up
cd $PROJ
rm efj.py efjgui.pyw
