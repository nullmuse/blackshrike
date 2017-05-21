from scapy.all import * 
import re

target = '5c:57:1a:b8:26:d0'

ap_list = []

def packet_process(pkt):
   global ap_list
   if pkt.haslayer(Dot11):
      if pkt.type == 0 and pkt.subtype == 8:
         if pkt.addr2 not in ap_list:
            ap_list.append(pkt.addr2)
            print "AP MAC {0} SSID {1}".format(pkt.addr2,pkt.info)


def load_mon():
   mon_interface = [] 
   with open("/proc/net/dev","r") as f:
      for line in f.readlines():
         if re.search(r'mon[0-9]+',line):
            print "Found airmon-ng interface..",line.split(":")[0].strip()
            mon_interface.append(line.split(":")[0].strip())
   


sniff(iface=mon_int, prn=packet_process)

