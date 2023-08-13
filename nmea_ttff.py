""" Simple NMEA processing to get statistics of intitialization
"""

import sys
import re
from datetime import datetime, date, time
import pandas as pd
import warnings

def checksum(buf):
    """ check nmea checksum on line """
    cs = ord(buf[1])
    for ch in buf[2:-3]:
        cs ^= ord(ch)
    return cs

def nmea2deg(nmea):
    """ convert nmea angle (dddmm.ss) to degree """
    w = nmea.split('.')
    return int(w[0][:-2]) + int(w[0][-2:]) / 60.0 + int(w[1]) / 600000000.0

def nmeatime(d, t):
    """ convert date time given as strings to datetime object """
    t = datetime.strptime(d + t, "%Y%m%d%H%M%S.%f")
    return t

warnings.filterwarnings("ignore")

fin = 'teto_201215c.nmea'
fin = 'test20230722045851.nmea'
if len(sys.argv) > 1:
    fin = sys.argv[1]   # get input file from command line

# open input file
fi = open(fin, 'r')

#open output file
#fo = open('nmea_stat.txt', 'a')


n = 0
date0 = None
first_epoch = None
first_fix = None
starting = None
df = pd.DataFrame(columns = ["datetime", "lat", "lon", "ele", "nsat"])

for line in fi:
    line = line.strip()
    n += 1
    if hex(checksum(line))[2:].upper() != line[-2:]:
#        print("Chechsum error: " + line)
        continue
    if re.match('\$..ZDA', line):
        gga = line.split(',')
        date0 = gga[4] + gga[3] + gga[2]
    if re.match('\$..GNS', line):
        gns = line.split(',')
        if date0 is None:
            continue
        if len(gns[1]):
            time = nmeatime(date0, gns[1])
            if first_epoch is None:
                first_epoch = time
                #print('{:%Y-%m-%d %H:%M:%S}'.format(first_epoch))
            
            if len(gns[2]):
                lat = nmea2deg(gns[2])
                if gns[3].upper() == 'S':
                    lat *= -1
                lon = nmea2deg(gns[4])
                if gns[5].upper() == 'W':
                    lon = 360 - lon
                height = float(gns[9]) + float(gns[10])
                

                nsat = int(gns[7])
                hdop = float(gns[8])
                age = float("nan")
                if len(gns[11]):
                    age = float(gns[11])
            
            sol_mode = gns[6]
            if "RRRR" in sol_mode:
                df = df.append({'datetime' : time, 'lat' : lat, 'lon' : lon, 'ele' : height, 'nsat' : nsat},
                    ignore_index = True)

            if first_fix is None and "RRRR" in sol_mode and starting is not None:
                
                first_fix = time
                #print('{:%Y-%m-%d %H:%M:%S}'.format(first_fix))
                init_time = (first_fix - first_epoch).total_seconds()
                if init_time > 0:
                    outp = '{:%Y-%m-%d %H:%M:%S},{:.8f},{:.8f},{:.3f},{:d},{:.1f},{:.3f},{:.3f}'.format(time, lat, lon, height, nsat, init_time, hdop, age)
    if re.match('\$..TXT', line):
        txt = line[:-3].split(',')
        msg = txt[4]
        if "Starting" in msg:
            starting = msg
            
        #fo_txt.write('{:%Y-%m-%d %H:%M:%S},{:s}\n'.format(time, msg))

fi.close()
if first_fix:
    print('{:s},{:d},{:.3f},{:.3f}'.format(outp, df.shape[0], df['ele'].mean(), df['ele'].std()))
#print('{:d} lines read in {:s}\n'.format(n, fin))


