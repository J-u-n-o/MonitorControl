from pathlib import Path
import sys
import os


import time
import psutil
from ctypes import *


def getPID(processName):
    for proc in psutil.process_iter():
        try:
            if processName.lower() in proc.name().lower():
                return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return None


def getGDIcount(PID):
    PH = windll.kernel32.OpenProcess(0x400, 0, PID)
    GDIcount = windll.user32.GetGuiResources(PH, 0)
    windll.kernel32.CloseHandle(PH)
    return GDIcount


def main1():
    #PID = getPID('Outlook')
    PID = os.getpid()

    while True:
        GDIcount = getGDIcount(PID)
        print(f"{time.ctime()}, {GDIcount}")
        time.sleep(1)


if __name__ == '__main__':
    main1()
