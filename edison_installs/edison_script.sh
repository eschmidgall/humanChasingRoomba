#!/bin/bash

opkg install libv4l_1.0.1-r0_core2-32.ipk mjpg-streamer_r182-r0_core2-32.ipk
tar xvzf setuptools-18.3.1.tar.gz
cd setuptools-18.3.1
python setup.py install
cd ..
unzip bunch-1.0.1.zip
cd bunch-1.0.1/
python setup.py install
cd ..
tar xvzf pyserial-2.7.tar.gz
cd pyserial-2.7/
python setup.py install
cd ..
tar xvzf python-jsonrpc-0.7.12.tar.gz
cd python-jsonrpc-0.7.12
python setup.py install
cd ..
