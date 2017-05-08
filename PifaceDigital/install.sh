#!/bin/sh

cp PifaceDigital.py /usr/local/bin

useradd --system pifacedigital
usermod -a -G spi pifacedigital
usermod -a -G gpio pifacedigital

mkdir /var/lib/pifacedigital
chown -R pifacedigital:pifacedigital /var/lib/pifacedigital
chmod -R 0755 /var/lib/pifacedigital 

########
# init.d DOES NOT WORK !!!
#cp ./etc/init.d/pifacedigital /etc/init.d/pifacedigital
#chmod 755 /etc/init.d/pifacedigital
#update-rc.d pifacedigital defaults

#########
# systemd
cp pifacedigital /etc/default
cp pifacedigital.service /etc/systemd/system
systemctl daemon-reload
systemctl enable pifacedigital
