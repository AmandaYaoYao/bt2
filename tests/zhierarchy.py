import threading
from subprocess import Popen, PIPE
import time


def popenAndCall(onExit, *popenArgs, **popenKWArgs):
    """
    Runs a subprocess.Popen, and then calls the function onExit when the
    subprocess completes.

    Use it exactly the way you'd normally use subprocess.Popen, except include a
    callable to execute as the first argument. onExit is a callable object, and
    *popenArgs and **popenKWArgs are simply passed up to subprocess.Popen.
    """
    def runInThread(onExit, popenArgs, popenKWArgs):
        proc = Popen(*popenArgs, **popenKWArgs)
        proc.wait()
        onExit()
        return
	
    thread = threading.Thread(target=runInThread,
	                          args=(onExit, popenArgs, popenKWArgs))

    thread.start()

    return thread 

def onExit():
	print("Success baby.")

p = Popen(["sudo", "python", "zplay.py", "hi"], shell=False, stdin=PIPE, stdout=PIPE)
time.sleep(10)
p.terminate()