#!/bin/bash

EDISON_IP=$1

scp * root@$EDISON_IP:
ssh root@$EDISON_IP ./edison_script.sh
