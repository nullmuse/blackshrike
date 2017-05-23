import ps_drone
import time
import telnetlib

#Written by system1337 


def move_box(drone):
    drone.moveForward()
    time.sleep(2)
    drone.moveRight()
    time.sleep(2)
    drone.moveBackward()
    time.sleep(2)
    drone.moveLeft()
    time.sleep(2)
    drone.stop()


def led_show(drone):
    drone.led(3,7,2)
    time.sleep(2)
    drone.led(2,7,2)
    time.sleep(2)
    drone.led(1,7,2)
    time.sleep(2)
    drone.led(2,7,2)
    time.sleep(2)
    drone.led(3,7,2)

def kill_drone(drone):
    set_altitude(drone, 100)
    t = telnetlib.Telnet(drone.DroneIP)
    t.write('reboot\n')
    drone.anim(16, 15)
    time.sleep(10)


def safe_startup(drone):
    drone.startup()  # Connects to drone and starts subprocesses
    drone.reset()  # Always good, at start
    while drone.getBattery()[0] == -1:
        time.sleep(0.5)  # Waits until the drone has done its reset
    time.sleep(0.5)  # Give it some time to fully awake


def finish(drone):
    drone.land()
    drone.shutdown()


def short_demon(drone):
    drone.led(3,7,2)

def show_off(drone):
    set_altitude(drone, 400)
    drone.anim(16, 10)
    time.sleep(6)
    set_altitude(drone, 400)
    drone.anim(17, 10)
    time.sleep(6)
    drone.anim(18, 10)
    time.sleep(4)
    drone.anim(19, 5)


def set_altitude(drone, height):
    data_count = drone.NavDataCount
    end = False
    while end is False:
        while drone.NavDataCount == data_count:
            time.sleep(0.01)  # Wait for NavData
        if drone.getKey():
            end = True
        data_count = drone.NavDataCount
        current_altitude = drone.NavData["demo"][3]
        if current_altitude >= height - 10 and current_altitude <= height + 10:
            drone.stop()
            end = True
        elif current_altitude < height:
            drone.moveUp(1.0)
        elif current_altitude > height:
            drone.moveDown(0.5)
        time.sleep(0.4)
        print('Current Altitude is {}'.format(current_altitude))

def demon_drone():
    zombie = ps_drone.Drone()
    zombie.startup()
    zombie.useDemoMode(False)
    short_demon(zombie)
    return
    time.sleep(1)
    zombie.getNDpackage(["demo"])
    time.sleep(1)
    zombie.setConfig("control:altitude max","600")
    time.sleep(1)
    set_altitude(zombie, 400)
    led_show(zombie)
    #while zombie.getBattery()[0] > 25:
    show_off(zombie)
    kill_drone(zombie)

#attack_drone.takeoff()
#time.sleep(4)
#set_altitude(attack_drone, 400)
#print(attack_drone.getBattery())
#kill_drone(attack_drone)
#print(attack_drone.getBattery())
#finish(attack_drone)
#show_off(attack_drone)
#attack_drone.land()
#finish(attack_drone)
