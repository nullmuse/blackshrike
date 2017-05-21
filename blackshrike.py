from scapy.all import * 
import re
import os 

target = '5c:57:1a:b8:26:d0'

ap_list = []

def initialize_monitor():
   wifi_file="/proc/net/wireless"
   if os.path.exists(wifi_file):
        with open(wifi_file) as f:
        for line in f.readlines():
                if not re.search(r'Inter-',line) and not re.search(r'face',line):
                    iface=line.split(":")[0]
   if iface:
        print 'Initializing monitor mode [airmon method]'
        os.system('airmon-ng start {0}'.format(iface.strip()))
   


def packet_process(pkt):
   global ap_list
   if pkt.haslayer(Dot11):
      if pkt.type == 0 and pkt.subtype == 8:
         if pkt.addr2 not in ap_list:
            ap_list.append(pkt.addr2)
            print "AP MAC {0} SSID {1}".format(pkt.addr2,pkt.info)
            

def stop_scan():
   global ap_list
   global target
   if target in ap_list:
      return True
   else:
      return False 

def load_mon():
   mon_interface = [] 
   with open("/proc/net/dev","r") as f:
      for line in f.readlines():
         if re.search(r'mon[0-9]+',line):
            print "Found airmon-ng interface..",line.split(":")[0].strip()
            mon_interface.append(line.split(":")[0].strip())
   return mon_interface


def seek_target():

   mons = load_mon() 
   sniff(iface=mons[0], prn=packet_process, stop_filter=stop_scan)

