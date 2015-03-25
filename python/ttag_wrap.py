import ttag
import numpy as np
import time
import shutil

def openttag(toFile = None):
    fromFile = '/mnt/odrive/HPD/ShanePyStuff/scripts/UQDttagger2/ttag/UQD/src/uqd.uqcfg'
    ttnumber = ttag.getfreebuffer()-1
    print "ttnumber: ", ttnumber
    buf = ttag.TTBuffer(ttnumber)  #Opens the buffer
    buf.tagsAsTime = False
    #buf.start()
    if toFile != None:
      shutil.copyfile(fromFile, toFile)
    return buf

def cleanUp(buf):
    print "Cleaning"
    buf.stop()

def getCnts_nowait(Tacq,CoincidenceWindow, gate, heraldChan, buf):
    x = buf.coincidences(Tacq, CoincidenceWindow)
    xx = buf.coincidences(Tacq, CoincidenceWindow, gate = gate, heraldChan = heraldChan)
    cnts_single = x[0:8,8:16]
    cnts_coin = xx[0:8,8:16]
    return cnts_single, cnts_coin

def getCnts(Tacq, CoincidenceWindow, gate, heraldChan, buf):
    time.sleep(Tacq)
    return getCnts_nowait(Tacq, CoincidenceWindow, gate, heraldChan, buf)

if __name__ == '__main__':
  toPath = './test.dat'
  buf = openttag(toPath)
