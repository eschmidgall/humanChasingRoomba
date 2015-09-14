#!/bin/bash
EDISON_IP=$1

scp launch_streamer.sh jsonrpcRoombaServer.py roomba_side_code.sh root@$EDISON_IP:
ssh root@$EDISON_IP ./roomba_side_code.sh
sleep 2
while true; do
    python ./opencv_code.py $EDISON_IP
done
