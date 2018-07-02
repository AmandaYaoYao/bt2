
#!/usr/bin/env python

# Dependencies:
# sudo apt-get install -y python-gobject

import time
import logging
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

#Pseudo -- If player_path2 then we know there's 2 players
    #we should check current signal -> Is it playing? 
    #we should replace it with paused if it is
        #We should let the thing know that we have this guy waiting to play next
        #We should look for signal that something has changed on player one (when next track happens)
        #Then we should play the player 2 song again
        #When should we add signal receiver to player 2? 
        #should we turn player 1 to player 2 and V.V. ? 
        # WHat if we return from find player and call this if then player thing? 
def ifPlayer(lst):
    player_path = lst[0]
    player_path2 = lst[1]

    if player_path2:
       print(player_path2)
       obj = self.bus.get_object('org.bluez', player_path2)
       player_properties2 = obj.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
       print('below here is obj.status')
       if player_properties2["Status"] == 'playing':
            print("they're both playing now")
            obj.Pause(dbus_interface=PLAYER_IFACE)
       print('END STATUS')

    if player_path:
            self.connected = True
            self.getPlayer(player_path)
            player_properties = self.player.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
            if "Status" in player_properties:
                self.status = player_properties["Status"]
            print('below is the original status')
            print(self.status)
            print('END GOOD STATUS')
            if "Track" in player_properties:
                self.track = player_properties["Track"]

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

        self.findPlayer()
        self.updateDisplay()

    def start(self):
        """Start the BluePlayer by running the gobject Mainloop()"""
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def end(self):
        """Stop the gobject Mainloop()"""
        if (self.mainloop):
            self.mainloop.quit();
    
    

    def findPlayer(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

       #Literally no idea why its like this
	player_list = []
        player_path = None
        for path, interfaces in objects.iteritems():
            if PLAYER_IFACE in interfaces:
		#print(player_list)
		#print(path)
           	player_list += [path]

        #this if player call calls the function in 
        return ifPlayer(player_list)
		

    def getPlayer(self, path):
        """Get a media player from a dbus path, and the associated device"""
        self.player = self.bus.get_object("org.bluez", path)
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
                if changed["Connected"]:
                    self.findPlayer()
        elif iface == "MediaPlayer1":
            if "Track" in changed:
                self.track = changed["Track"]
                self.updateDisplay()
            if "Status" in changed:
                self.status = (changed["Status"])
    def updateDisplay(self):
        if self.player:
            if "Artist" in self.track:
                print(self.track["Artist"])
            if "Title" in self.track:
                print(self.track["Title"])
        else:
            print("Waiting for media player")

    def next(self):
        self.player.Next(dbus_interface=PLAYER_IFACE)

    def previous(self):
        self.player.Previous(dbus_interface=PLAYER_IFACE)

    def play(self):
        self.player.Play(dbus_interface=PLAYER_IFACE)

    def pause(self):
        self.player.Pause(dbus_interface=PLAYER_IFACE)

if __name__ == "__main__":
    player = None

    try:
        player = BluePlayer()
        player.start()
    except KeyboardInterrupt as ex:
        print("\nBluePlayer cancelled by user")
    except Exception as ex:
        logging.exception("message")
	#print("How embarrassing. The following error occurred {}".format(ex))
    finally:
        if player: player.end()
