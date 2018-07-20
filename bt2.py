
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
    player_list = []
    connected2 = None
    status2 = None
    needs_flipped = False

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

    #how do main loops work instead of other loop types? 
    def start(self):
        """Start the BluePlayer by running the gobject Mainloop()"""
        self.mainloop = gobject.MainLoop()
        self.mainloop.run()

    def end(self):
        """Stop the gobject Mainloop()"""
        if (self.mainloop):
            self.mainloop.quit();
    
    #Pseudo -- If player_path2 then we know there's 2 players
        #we should replace it with paused if it is not 
        #We should let the thing know that we have this guy waiting to play next
        #We should look for signal that something has changed on player one (when next track happens)
        #Then we should play the player 2 song again
        #When should we add signal receiver to player 2? 
        #should we turn player 1 to player 2 and V.V. ? 
        #maybe add a nice needs flipped variable to tell if stuff needs to get flipped or not
        #NEED TO HANDLE ONly one connection
    def ifPlayer(self, lst):
<<<<<<< HEAD
        if lst[0]:
            player_path = lst[0]
        if lst[1]:
            player_path2 = lst[1]
=======
        player_path = None
	player_path2 = None
	#The 0 length case seems handled 
	if len(lst) ==  1: 
           player_path = lst[0]
        if len(lst) == 2:
           player_path = lst[0]
	   player_path2 = lst[1]
>>>>>>> 4c3b845d6159f214336d956f01c37dfe109bd7db

        #Changed by getting rid of print(path2)
        #Now making a call to player2
        if player_path2:
           self.connected2 = True
           self.player2(player_path2)

        if player_path:
                self.connected = True
                self.getPlayer(player_path)
                player_properties = self.player.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
                if "Status" in player_properties:
                    self.status = player_properties["Status"]
                print('below is player1s status')
                print(self.status)
                if "Track" in player_properties:
                    self.track = player_properties["Track"]

    #in playerhandler2 i set obj.connected, which probably should not happen realistically,
    #means that we do not need to set
    #gonna fuck round with these'r objects shortly and see what happens
    def player2(self, path):
           obj = self.bus.get_object('org.bluez', path)
           obj.connect_to_signal("Player2Sig", self.playerHandler2, dbus_interface="org.freedesktop.DBus.Properties", arg0="path")
           obj.Pause(dbus_interface=PLAYER_IFACE)
           player_properties2 = obj.GetAll(PLAYER_IFACE, dbus_interface="org.freedesktop.DBus.Properties")
           if "Status" in player_properties2:
                self.status2 = player_properties2["Status"]
           if player_properties2["Status"] == 'playing':     
                print("Just Paused Player 2")
                obj.Pause(dbus_interface=PLAYER_IFACE)
                print("This should be the status of player2 now:")
                print(player_properties2["Status"])
                self.needs_flipped = True
                #does obj work here?
		#really not sure  bout line below -- look at iot for error
         
    
    #if there's not 2 devices device connected though, what are we going to do? 
    #Should probably add a buttton for single player mode       
    def findPlayer(self):
        """Find any current media players and associated device"""
        manager = dbus.Interface(self.bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        #Literally no idea why its like this
        player_path = None
        for path, interfaces in objects.iteritems():
            if PLAYER_IFACE in interfaces:
                #indented this which was unexpected
               	self.player_list += [path]
        #this ifplayer call calls the function in 
        	self.ifPlayer(self.player_list)
		

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
        #print("Interface: {}; changed: {}".format(iface, changed))
        if iface == "Device1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
        elif iface == "MediaControl1":
            if "Connected" in changed:
                self.connected = changed["Connected"]
                if changed["Connected"]:
                    self.findPlayer()
        elif iface == "MediaPlayer1":
            #when the track changes, check if we need to update player orders
            if "Track" in changed:
                self.track = changed["Track"]
                if self.needs_flipped == True:
                    #NEED TO INTEGRATE THIS WITH FINDPLAYER WHICH HAS A FUCKED UP LIST ATM
                    self.player_list = [self.player_list[0], self.player_list[1]]
                    self.needs_flipped = False
                    ifPlayer(self.player_list)
                self.updateDisplay()
            if "Status" in changed:
                self.status = (changed["Status"])

    #Just made this noice old playerHandler2
    def playerHandler2(self, interface, changed, invalidated, path):
        """Handle relevant property change signals"""
        iface = interface[interface.rfind(".") + 1:]
	print('signal handsler 2 is working')
        #print("Interface: {}; changed: {}".format(iface, changed))
        if iface == "Device1":
            if "Connected" in changed:
                self.connected2 = changed["Connected"]
        elif iface == "MediaControl1":
            if "Connected" in changed:
                self.connected2 = changed["Connected"]
                if changed["Connected"]:
                    self.findPlayer()
        elif iface == "MediaPlayer1":
            if "Status" in changed:
                self.status2 = (changed["Status"])
                self.needs_flipped = True
                self.player2(self.player_list[1])

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
