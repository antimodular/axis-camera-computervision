export APP_NAME=mov-detector
export CAMERA_IP=192.168.1.193
DEVICE_RW=/dev/datacache0:rw

ENVS='DBUS_SYSTEM_BUS_ADDRESS=unix:path=/var/run/dbus/system_bus_socket'

SOCKETS="/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket \
	/var/run/statuscache:/var/run/statuscache"

for socket in $SOCKETS; do
	SOCK="$SOCK -v $socket:rw"
done


docker -H tcp://$CAMERA_IP run -it --privileged -e $ENVS --device=$DEVICE_RW --device=/dev/apex_0 $SOCK $APP_NAME 
