import os
import sys
import time
def info():
        print('''
Usage: shutdown [/t | /s | /r ]
    [/t xxx]

    No args    Display help. This is the same as typing /?.
    /?         Display help. This is the same as not typing any options.
    /s         Shutdown the computer.
    /r         Full shutdown and restart the computer.
    /t xxx     Set the time-out period before shutdown to xxx seconds.''')
if len(sys.argv) >= 3:
        if sys.argv[2] == "/t":
                time.sleep(int(sys.argv[3]))
        if sys.argv[1] == "/s":
                os.system("start /unix /sbin/poweroff")
        if sys.argv[1] == "/r":
                os.system("start /unix /sbin/reboot")
if len(sys.argv) == 2:
        if sys.argv[1] == "/?":
                info()
        if sys.argv[1] == "/s":
                os.system("start /unix /sbin/poweroff")
        if sys.argv[1] == "/r":
                os.system("start /unix /sbin/reboot")
if len(sys.argv) == 1:
        info()
