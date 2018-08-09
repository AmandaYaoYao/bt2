
#!/usr/bin/env python

# Dependencies:
# sudo apt-get install -y python-gobject
# if name== main works for our subprocesses so no need to change
# need to drop shit when ppl disconnect.
"""
Currently: If can get rid of sudo bluealsa player at right time, then neither will hear the wrong song
"""
import pause
import time
import signal
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject
import os

 # to run play with async call back
import threading
from subprocess import Popen, PIPE

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
    subp = None
    sublis = None

    def __init__(self):
        """Specify a signal handler, and find any connected media players"""
        gobject.threads_init()
        # might ned this
        dbus.mainloop.glib.threads_init()
        dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)


        self.bus = dbus.SystemBus()

        # self.bus.add_signal_receiver(self.playerHandler,
        #         bus_name="org.bluez",
        #         dbus_interface="org.freedesktop.DBus.Properties",
        #         signal_name="PropertiesChanged",
        #         path_keyword="path")

        self.findPlayer()

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

        for path, interfaces in objects.iteritems():
            if PLAYER_IFACE in interfaces:
                #indented this which was unexpected
                self.player_list += [path]

        self.runPlays()


    def runPlays(self):
        player_path = None
        player_path2 = None
        #The 0 length case seems handled 
        if len(self.player_list) ==  1: 
           player_path = self.player_list[0]
        # this will break with three devices immediately
        if len(self.player_list) == 2:
           player_path = self.player_list[0]
           player_path2 = self.player_list[1]


        #Changed by getting rid of print(path2)
        #Now making a call to player2
        if player_path2:
            self.connected2 = True
            cmnd = ["sudo","python", "pause.py"] 
            cmnd.append(player_path2)
            self.subp = Popen(cmnd, shell=False, stdout=PIPE, preexec_fn=os.setpgrp)
            
          

        if player_path:
           print(player_path)
	   self.connected = True
	       # this guy makes the call to play
           cmds = ["sudo","python", "play.py"] 
           cmds.append(player_path)
           # appending indicator that this is the only player so that we never exit if not
           cmds.append("notonlyplayer")

           # need to open our listener
           lis = ["sudo", "bluealsa-aplay"]
           #makes everything split on these underscores
           path = player_path.split('_')
           #gets rid of everything before dev name, fixes end, then turns _ to :
           path.pop(0)
           path[5] = path[5][:2]
           path = ':'.join(path)
           #add cleaned devname to our thing.
           lis.append(path)
           #does sudobluealsa thing
           self.sublis = Popen(lis, shell=False, stdout=PIPE, preexec_fn=os.setpgrp)
           #opens and calls stuff
           self.popenAndCall(self.flipPlayer, cmds, shell=False, stdout=PIPE)

    # obviously nonsensical at the moment.
    def flipPlayer(self):
        print("flipplayer called")   
	# end this guy
        if self.subp:
            print("hey you institiuted this print to show you that killing is happening on pause,py. ")
	   self.subp.kill()
           os.killpg(self.subp.pid, signal.SIGKILL)
           #Reset subp at end be careful of this tho.
           self.subp = None

        if self.sublis
            print("hey you institiuted me to show you that we killed listener ")
       self.sublis.kill()
           os.killpg(self.sublis.pid, signal.SIGKILL)
           #Reset subp at end be careful of this tho.
           self.sublis = None

        print("if you didnt see a print about killiing uhoh")
        # let's worry about this later too.
    	# if len(self.player_list) ==  1: 
        # only play current
        # player_path = self.player_list[0]
        # this will break with three devices immediately
        if len(self.player_list) == 2:
           player_path = self.player_list[0]
           player_path2 = self.player_list[1]
           self.player_list = [player_path2, player_path]
        # migt have been missing runplays call idiot
        self.runPlays()

    def popenAndCall(self, onExit, *popenArgs, **popenKWArgs):
	    """
	    Runs a subprocess.Popen, and then calls the function onExit when the
	    subprocess completes.

	    Use it exactly the way you'd normally use subprocess.Popen, except include a
	    callable to execute as the first argument. onExit is a callable object, and
	    *popenArgs and **popenKWArgs are simply passed up to subprocess.Popen.
	    """
	    print("popen and called called")
	    def runInThread(onExit, popenArgs, popenKWArgs):
	        proc = Popen(*popenArgs, **popenKWArgs)
		proc.wait()
	        onExit()
	        return
		
	    thread = threading.Thread(target=runInThread,
		                          args=(onExit, popenArgs, popenKWArgs))

	    thread.start()

	    return thread 
	 

if __name__ == "__main__":
    player = None

    try:
        player = BluePlayer()
        player.start()
    except KeyboardInterrupt as ex:
        print("\nBluePlayer cancelled by user")
    except Exception as ex:
        print("How embarrassing hierarchy. The following error occurred {}".format(ex))
    finally:
        if player: player.end()
