#!/usr/bin/env python

# Dependencies:
# sudo apt-get install -y python-gobject

import time
import signal
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject

SERVICE_NAME = "org.bluez"
AGENT_IFACE = SERVICE_NAME + '.Agent1'
ADAPTER_IFACE = SERVICE_NAME + ".Adapter1"
DEVICE_IFACE = SERVICE_NAME + ".Device1"
PLAYER_IFACE = SERVICE_NAME + '.MediaPlayer1'
TRANSPORT_IFACE = SERVICE_NAME + '.MediaTransport1'

class BluePlayer():
    bus = None
    mainloop = None
    device = None
    deviceAlias = None
    player = None
    connected = None
    state = None
    status = None
    track = []
    addy = None

    def __init__(self):
        """Specify a signal handler, and find any connected media players"""
        gobject.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


        self.bus = dbus.SystemBus()

        self.bus.add_signal_receiver(self.playerHandler,
                bus_name="org.bluez",
                dbus_interface="org.freedesktop.DBus.Properties",
                signal_name="PropertiesChanged",
                path_keyword="path")


    def setAddy(self, path):
        self.addy = path

    def start(self):
        """Start the BluePlayer by running the gobject Mainloop()"""
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()
        self.getPlayer(self.addy)

    def end(self):
        """Stop the gobject Mainloop()"""
        if (self.mainloop):
            self.mainloop.quit();

    def getPlayer(self, path):
        """Get a media player from a dbus path, and the associated device"""
        self.player = self.bus.get_object("org.bluez", path)
        print("Player gotten:")
	print self.player
        self.pause()
        device_path = self.player.Get("org.bluez.MediaPlayer1", "Device", dbus_interface="org.freedesktop.DBus.Properties")
        self.getDevice(device_path)

    def getDevice(self, path):
        """Get a device from a dbus path"""
        self.device = self.bus.get_object("org.bluez", path)
        self.deviceAlias = self.device.Get(DEVICE_IFACE, "Alias", dbus_interface="org.freedesktop.DBus.Properties")

    def playerHandler(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        iface = interface[interface.rfind(".") + 1:]
#        print("Interface: {}; changed: {}".format(iface, changed))

        if iface == "Device1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
        elif iface == "MediaControl1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
                
                # @TODO Were gonna need to do something if this guy disconnects in the future!
                # if changed["Connected"]:
                #     self.findPlayer()
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                self.pause()
                self.track = changed["Track"]
                self.updateDisplay()
            if "Status" in changed:
                self.pause()
                self.status = (changed["Status"])

    def next(self):
        self.player.Next(dbus_interface=PLAYER_IFACE)

    def previous(self):
        self.player.Previous(dbus_interface=PLAYER_IFACE)

    def play(self):
        self.player.Play(dbus_interface=PLAYER_IFACE)

    def pause(self):
       print("her3e comes the player")
       print(self.player)
       self.player.Pause(dbus_interface=PLAYER_IFACE)

player = None

def run(address):
    player = None    

    try:
        player = BluePlayer()
        player.setAddy(address)
        player.start()
    except KeyboardInterrupt as ex:
        print("\nBluePlayer cancelled by user")
    except Exception as ex:
        print("How embarrassing. The following error occurred {}".format(ex))
    finally:
        if player: player.end()

def end():
    global player
    player.end()

