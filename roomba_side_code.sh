#!/bin/bash

nohup ./launch_streamer.sh 2>/dev/null  >/dev/null </dev/null &
nohup python ./jsonrpcRoombaServer.py 2>/dev/null >/dev/null </dev/null  &
