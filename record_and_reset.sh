#!/bin/sh

#shell script to get RTCM RTK corrections and transfer to an u-blox f9p RTK receiver and record NMEA data
#all communication is based upon rtklib demo5
#restart ublox gnss unit at every n seconds
#monitor RTK initialisation time and position accuracy
#developed by Bence Takács, takacs.bence@emk.bme.hu, 13 August 2023

while :
do
  #output file with path
	out_file="$(date +'/home/pi/rtk_monitor/data/test%Y%m%d%H%M%S.nmea' -u)"
  #reset ublox gnss unit
	str2str -in serial://ttyACM0 -c /home/pi/rtk_monitor/ubx_reset.cmd > $out_file 2> /dev/null &
	sudo sleep 1 && pkill -f str2str 
	#RTCM corrections from gpsmet.agt.bme.hu caster
  #str2str -in ntripcli://username:pwd@gpsmet.agt.bme.hu:2101/BUTE0 -b 1 -out serial://ttyACM0:115200#5000 2>/dev/null & 	
  #RTCM corrections from gnssnet.hu, Göd
  #str2str -in ntripcli://username:pwd@gntrip1.gnssnet.hu:2101/SGO_PRS3.2 -p 47.680450 19.127756 180.0 -b 1 -out serial://ttyACM0:115200#5000 2>/dev/null & 	
  #RTCM corrections from gnssnet.hu, Forduló köz
  str2str -in ntripcli://username:pwd@gntrip1.gnssnet.hu:2101/SGO_PRS3.2 -p 47.566128 19.008104 180.0 -b 1 -out serial://ttyACM0:115200#5000 2>/dev/null & 	
	str2str -in tcpcli://localhost:5000 >> $out_file 2>/dev/null &
  #collect data for 150 seconds
	sudo sleep 150 && pkill -f str2str 
  #process file and append results
  python3 /home/pi/rtk_monitor/nmea_ttff.py $out_file >> /home/pi/rtk_monitor/nmea_stat.txt
  #upload data to server
	scp $out_file username@152.66.5.194:ublox/data
	scp /home/pi/rtk_monitor/nmea_stat.txt username@152.66.5.194:ublox
done
