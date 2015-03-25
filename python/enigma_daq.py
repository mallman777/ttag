import datetime
import numpy as np
import os
def createDatafolder():
    format = '%Y_%m_%d'
    folder = '/hdd/%s/'%datetime.datetime.today().strftime(format)
    print folder
    # creating directory for data
    dirCnt=1
    while True:
        dataPath = folder+'run%02d/'%dirCnt
        #print dataPath
        try:
          os.makedirs(dataPath)
          break
        except:
          dirCnt += 1
    print 'dataPath:',dataPath
    return dataPath,dirCnt

def tags2file(dataPath, tup,cnt):
    fnameTags = 'tag_%06d.bin'%cnt
    fnameChans = 'chan_%06d.bin'%cnt
    ##print 'Saving to %s, %s'%(fnameTags, fnameChans)
    fTags = open(dataPath+fnameTags,'wb')
    fChans = open(dataPath+fnameChans,'wb')
  
    chans = tup[0]  #Single byte unsigned integer
    tags = tup[1] #8 byte unsigned integer
    chans.tofile(fChans)
    tags.tofile(fTags)
    fChans.close()
    fTags.close()


def write2file(dataPath, fname, cnts, xo, yo, cnt):
    #print 'Saving to %s'%(fname)

    fp = open(dataPath+fname,'a')
    np.savetxt(fp, cnts, fmt = '%7d')
    fp.write('#x:%5f  y:%5f  cnt:%d\n'%(xo,yo,cnt))



