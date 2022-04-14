## Setup the camera

Make sure that the camera has docker installed: https://github.com/AxisCommunications/docker-acap

### Disable TLS and enable SD card for docker:
Go in System -> Plain config -> search -> "Docker"  disable TLS, and enable SD card support.
These instructions might be a bit different as we are using two different models of cameras. In case you have problems finding it, feel free to ask.
NOTE: TLS can be disabled to avoid some extra boring configuration steps, but only if the camera is in a private network. If the camera is exposed TLS MUST BE ENABLED, otherwise it will get hacked in a couple of days.


### Start docker

Go in Apps -> Turn on Docker Daemon
Check in the log that you see the string:

dockerdwrapper[2791441]: time="2022-04-12T00:00:22.290724040+02:00" level=info msg="API listen on [::]:2375"


## Build deploy and run the container
```sh
export AXIS_TARGET_IP=<actual camera IP address>
export DOCKER_PORT=2375
export APP_NAME=mov-detector
```
```sh
# Build and upload inference client for camera
docker build . -t $APP_NAME 
docker save $APP_NAME | docker -H tcp://$AXIS_TARGET_IP:$DOCKER_PORT load
docker -H tcp://$AXIS_TARGET_IP:$DOCKER_PORT run -it $APP_NAME
docker-compose -H tcp://$AXIS_TARGET_IP:$DOCKER_PORT up
```

You can also run build_deploy_and_run.sh in alternative.

## Output of the ACAP
The acap will send UDP packets on the configurable address in the script, to capture the output, you can set as UDP_IP your own IP and run on a terminal 
```sh
nc -ul <your_IP> 5005
```
While the ACAP is running on the camera.

Another way to see the results is to set the variable SAVE_OUTPUT to "True" Note: This will slow down the ACAP. In this way, the ACAP will save the frames.
To extract the frames from the container you can run
```sh
docker -H <CAMERA_IP> ps  
```
to find the container ID
```sh
docker -H <CAMERA_IP> cp <container ID>:/app/output ./
```
to download the captured frames.


