# Human Chasing Roomba!

Videos:

https://youtu.be/l4gq4lFw1t4

https://youtu.be/lB5RYD_y2E0

This project have been built as part of Geekcon 2015.

##Hardware setup:

Our setup is built from:
- A Roomba (we used Roomba 595, any Series 500 and above Roomba should work)
- An Edison Board computer (Sparkfun kit, was donated by Intel, you can build a similar setup using Raspberry Pi)
- A CD-4050-BE buffer chip, boosting the UART signal power from the Edison to the Roomba.
- A USB car charger as a 12-20V to 5V converter, powering the Edison and the buffer chip
- A PS/2 Keyboard cable interfacing the Roomba Open Interfact port. Extract the plastic middle pin to make it mechanically fit. You can use other mini-DIN 7 or mini-DIN 8 cables for this connection.
- A webcam (we used a Logitech HD webcam) + a USB OTG adapter to connect it to the Edison.
- A bluetooth speaker for sound effects
- A USB to micro-USB cable (powering the Edison)
- A USB cable (will be split open, extracting power to the CD-4050-B chip)
- A cardboard to hold the electronics on top of the roomba (cut to the form of the Roomba face board)
- Some packing materials and a stick to lift the camera up and keep it stable

The hardware installation is relatively straight forward:
- Switch the Sparkfun Edison GPIO board to use VSYS
- Build the stack of sparkfun boards for the Edison - Edison, sparkfun base-board, GPIO board, battery board.
- Connect the Edison battery board to the USB car charger, to ensure stable power supply
- Connect the UART TX pin of the Edison from the GPIO board to pin 3 on the CD-4050-B chip
- Open up a USB cable, detect the 5V and ground pins (should be connected to the pins in the edges of the USB connector)
- Connect the Vcc of the CD-4050-B chip (Pin 1) to the 5V pin of the USB cable
- Connect the ground of the CD-4050-B (Pin 8) to the ground of the USB cable, and to the GND pin of the Edison GPIO board.
- Connect pin 2 of the CD-4050-B chip to pin 3 of the Roomba Open Interface connector (see http://irobot.lv/uploaded_files/File/iRobot_Roomba_500_Open_Interface_Spec.pdf page 3 for pinout details)
- Connect the USB car charger to the power and ground pins of the Roomba Open Interface (power is either pin 1 or 2, ground is pins 6,7 and casing). Make sure to get the polarity right. Doing this step wrong will cause capacitors to explode. Check the pins with a volt meter before connecting!
- Connect the webcam to the Edison OTG port.
- The webcam should be lifted reasonably high from the roomba in order for it to find human faces. We used a stick and some packaging material to stabilize it high enough in the air on top of the roomba. You can figure out your own creative ideas for such thing. Maybe a roomba-drone pair for coordinated air and ground attack?

##SW Installation:
- The Edison was running Linux Yocto, version WW25.5.
- Configure the Edison board to be an access point, using "configure_edison --enableOneTimeSetup --persist" on its shell. Setup a password to enable SSH.
- Connect to the Edison access point, take note of the Edison IP. Replace "EDISON_IP" with this IP address in the following steps.
- Deploy the needed SW on the Edison by running "cd edison_installs; ./install_edison.sh EDISON_IP; cd .."
- Compile opencv, with the contrib libraries from https://github.com/shacharr/opencv and https://github.com/shacharr/opencv_contrib , tag geekcon_2015_code .
  * We used ubuntu 14.04 as our base machine for this.
  * You will need to have cmake installed, as well as bunch of other -dev packages. Internet claims that "sudo apt-get -y install libopencv-dev build-essential cmake git libgtk2.0-dev pkg-config python-dev python-numpy libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtiff4-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev libtbb-dev libqt4-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils unzip" will install everything you need.
  * I had to add a symbolic link from /opencv/modules/stitching/include/opencv2/xfeatures2d.hpp to opencv_contrib/modules/xfeatures2d/include/opencv2/xfeatures2d.hpp and from /opencv/modules/stitching/include/opencv2/xfeatures2d/ to opencv_contrib/modules/xfeatures2d/include/opencv2/xfeatures2d/ before compiling.
  * Putting this all together, the following extra-long one-liner should do all the compilation and installation for you: ``` sudo apt-get -y install build-essential cmake git libgtk2.0-dev pkg-config python-dev python-numpy libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtiff4-dev libjasper-dev libavcodec-dev libavformat-dev libswscale-dev libxine-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev libv4l-dev libtbb-dev libqt4-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev x264 v4l-utils unzip && mkdir opencv && cd opencv && git clone https://github.com/shacharr/opencv && cd opencv && git checkout geekcon_2015_code && cd .. && git clone https://github.com/shacharr/opencv_contrib && cd opencv_contrib && git checkout geekcon_2015_code && cd .. && mkdir opencv_build && cd opencv_build &&  cmake -D OPENCV_EXTRA_MODULES_PATH=`pwd`/../opencv_contrib/modules -D BUILD_opencv_reponame=OFF `pwd`/../opencv && make -j5 && sudo make -j5 install ```
- We use json-RPC for communicating with the Roomba. Run "sudo pip install python-jsonrpc" to install the needed library.
- For audio, install festival on your computer, and configure the default audio out to be a portable bluetooth speaker installed on the Roomba.
- Start the code by running "./run_all.sh EDISON_IP"
- Press escape if the roomba is tracking something which is not useful. This can be done also to effectively stop the roomba (it will switch back to slowly turning around in the same place)

##Troubleshooting:

### Roomba not responding to serial commands

We have had such issue delaying us for about half a day. Check the following:
- Did you connect the right pin to the roomba UART? Are all connections well connected? To diagnose this, you can use single hard pins for the wires instead of connecting through a PS/2 plug, should work the same.
- Is your ground for all devices the same ground? Check resistance between the Roomba ground pin, the 4050 buffer chip ground pin and the Edison ground pin. All should have zero resistance between them.
- Does your power supply work as expected? Make sure the 4050 buffer chip is getting 5V supply voltage.
- Did you convert your Edison GPIO block to be in VSYS instead of 3.3V? Force a GPIO pin to high, and check the resulting voltage. 3.3V is bad, 4.2 and above is OK.
- Did you attempt to use a sparkfun level converter instead of a true buffer chip? The sparkfun level converter is not good. In our experience, it outputted a voltage of 2V when the GPIO pin was pulled to low and the Roomba was connected. This might have to do with a strong pullup resistor on the Roomba side. A good buffer chip did the trick there.
- The Edison board sometimes get the camera confused, try powering it completely off and on again to fix weird issues with the camera.
- SW crash happens from time to time, as we pulled basically a daily checkout of the opencv project. It should restart automatically in this case.
- Make sure you specified your Edison board IP address wherever it is listed "EDISON_IP". Also, make sure to set a password on your Edison to enable SSH ("configure_edison --password")
- The Edison base image only includes the drivers for uvc based webcams. For older webcams, you will need to compile the relevant kernel module by rebuilding your Edison kernel. Have a look at Intel's documentation for that.

##Logic and design:

The Edison on the Roomba is used to stream back video and relay commands for the Roomba from the controlling computer. The controlling computer is analyzing the video for human existence and targets the Roomba accordingly.

The video streaming is done using mjpg_streamer, using a trick based on code from http://petrkout.com/electronics/low-latency-0-4-s-video-streaming-from-raspberry-pi-mjpeg-streamer-opencv/ to feed the stream to OpenCV at low latency.

Control is done using a JSON-RPC server running on the Roomba. It supports left, straight, right and spin commands. The controlling computer is issuing these commands to keep tracking the target. The JSON-RPC server is translating these commands to the Roomba serial interface commands, abstracting these details from the network protocol.

The following logic is used on the controlling computer:
- If no target was found yet, spin the roomba slowly in place and search for faces (using OpenCV's haar-cascade for face detection).
- Once a face was found, stop the roomba for 0.5 seconds, check that face is still there.
- If face was not found, return to spinning around.
- If the face was found again, use a KCF tracker to track the area under the face in the video.
- For each image in which the area was tracked, compute the relative movement of the area in the video, compared to the running average of area center on the past (IIR filter on the mean-x value, with a single tap of 0.001).
- Depending on the relative movement, move left, right or straight until next image is processed.
- If image processing took longer than a frame capture would have taken, skip frames to make it even again.


##The legal corner

You are welcome to use our code under GPLv2.

We are using OpenCV code, and copied few files from OpenCV's source tree. Specifically, the haar cascade for face detection. Therefore, we need to include the following:




                          License Agreement
               For Open Source Computer Vision Library
                       (3-clause BSD License)

Copyright (C) 2000-2015, Intel Corporation, all rights reserved.
Copyright (C) 2009-2011, Willow Garage Inc., all rights reserved.
Copyright (C) 2009-2015, NVIDIA Corporation, all rights reserved.
Copyright (C) 2010-2013, Advanced Micro Devices, Inc., all rights reserved.
Copyright (C) 2015, OpenCV Foundation, all rights reserved.
Copyright (C) 2015, Itseez Inc., all rights reserved.
Third party copyrights are property of their respective owners.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  * Redistributions of source code must retain the above copyright notice,
    this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above copyright notice,
    this list of conditions and the following disclaimer in the documentation
    and/or other materials provided with the distribution.

  * Neither the names of the copyright holders nor the names of the contributors
    may be used to endorse or promote products derived from this software
    without specific prior written permission.

This software is provided by the copyright holders and contributors "as is" and
any express or implied warranties, including, but not limited to, the implied
warranties of merchantability and fitness for a particular purpose are disclaimed.
In no event shall copyright holders or contributors be liable for any direct,
indirect, incidental, special, exemplary, or consequential damages
(including, but not limited to, procurement of substitute goods or services;
loss of use, data, or profits; or business interruption) however caused
and on any theory of liability, whether in contract, strict liability,
or tort (including negligence or otherwise) arising in any way out of
the use of this software, even if advised of the possibility of such damage.
