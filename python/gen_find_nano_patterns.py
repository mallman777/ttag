import random
import numpy as np
phasemap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
phasemap = phasemap[:,1]
#SLMpath = './SLMPatterns/'
SLMpath = '/mnt/SLM/Dan/Find/Patterns/OrigSettings/'
SLMpath = '/mnt/SLM/Dan/FindNanowiresSERICALPORT/NanowireScanNOSCRAMBLE/Alice/'

phase_offset = 10000
#  Need to makedirs the SLMPath if necessary

def initial_phase(x0,y0, nrows):
  x = np.arange(nrows)
  y = np.arange(nrows)
  x,y = np.meshgrid(x,y)
  x = x-(nrows/2)-1
  y = y-(nrows/2)-1
  y0_idx = y0+nrows/2
  x0_idx = x0+nrows/2
  phase_xslope = -2.*np.pi / nrows * x0
  phase_yslope = -2.*np.pi / nrows * y0
  phase = phase_xslope * x + phase_yslope * y
  phase = np.mod(phase,2*np.pi)
  return phase

def initial_phase_orig2(x0,y0,nrows):
  pi = np.pi
  phase = np.zeros((512,512))
  k_x = 2*pi*np.arange(-256,256)/512.0
  k_y = 2*pi*np.arange(-256,256)/512.0
  #xo,yo = (1,1)
  """
  for i in range(phase.shape[0]):
    phase[i,:] += k_x*x0
  """
  phase = np.tile(k_x*x0, 512)
  """
  for i in range(phase.shape[1]):
    phase[:,i] += k_y*y0
  """
  phase += (k_y*y0).repeat(512)
  phase = np.mod(phase,2*np.pi)
  phase.shape=(512,512)
  return phase


def initial_phase_orig(x0,y0,nrows):
    pi = np.pi
    phase = np.zeros((512,512))
    k_x = 2*pi*np.arange(-256,256)/512.0
    k_y = 2*pi*np.arange(-256,256)/512.0
    #xo,yo = (1,1)
    for i in range(phase.shape[0]):
      phase[i,:] += k_x*x0
    for i in range(phase.shape[1]):
      phase[:,i] += k_y*y0
    phase = np.mod(phase,2*np.pi)
    return phase

def encrypt(seed, patres, encres):
    np.random.seed(seed)
    pattern = np.where(np.random.rand(encres,encres)<0.5, 0, 1)    
    expand = patres/encres
    phase = np.kron(pattern, np.ones((expand,expand)))
    return phase * np.pi
    #phase = initial_phase_orig(x0,y0,nrows)

def decrypt(ph,xshift,yshift, patres):
    phase = ph[:,::-1]
    pad = np.zeros((patres, patres))
    if yshift<0:
       submatrix = phase[:yshift,:]
    else:
       submatrix = phase[yshift:,:]
    if xshift<0:
       submatrix = submatrix[:,:xshift]
    else:
       submatrix = submatrix[:,xshift:]
    if yshift < 0 and xshift < 0:
      pad[-yshift:, -xshift:] = submatrix
    elif yshift > 0 and xshift > 0:
      pad[:-yshift, :-xshift] = submatrix
    elif yshift < 0 and xshift > 0:
      pad[-yshift:, :-xshift] = submatrix
    elif yshift > 0 and xshift < 0:
      pad[:-yshift,-xshift:] = submatrix
    else:
      pad = submatrix  
    phase = pad
    return phase
    
    
def get_rnd(T, nrows):
    noise = np.random.rand(nrows,nrows)*2*np.pi/T
    #noise = noise * T/normT
    return np.kron(noise, np.ones((512/nrows, 512/nrows)))
    #return noise

def write2file(phase, phasemap, path, namestr):
    phase = phase.T  #  convert so that the file written is the same as MATLAB
    phase_int = np.floor(phase.ravel() * (2**16 / (2*np.pi))).astype(int)%(2**16)
    phase_int = (phase_int + phase_offset)%(2**16)
    out = phasemap[phase_int]
    #print out[:2]
    #out = out.byteswap()
    out.tofile(path+'SLM_%s.dat'%namestr)

def interpolate2SLM(dataPath, xstart, xstep, ystart, ystep):
    IS = np.loadtxt(dataPath + 'interpSettings.txt')
    #print IS
    x = IS[:,2]*xstep + xstart
    y = IS[:,1]*xstep + ystart
    return np.vstack([x,y]).T

def getInterpSettings():
  dataPath = '/hdd/2015_03_11/run14/'
  IS = np.loadtxt(dataPath + 'interpSettings.txt')
  startx = 60
  starty = 60
  endx = 240
  endy = 240
  step = 2
  numpats = (endx-startx)+1
  settings = np.zeros((64,2))
  #print IS 
  for i in range(64):
    xinterp = IS[i,2]
    yinterp = IS[i,1]

    newx = startx + step*xinterp
    newy = starty + step*yinterp

    settings[i,0] = newx
    settings[i,1] = newy
  return settings

if __name__ == '__main__':
#  for x in range(114,209):
#    for y in range(114, 209):
#    for x in range(104,231,2):
#     for y in range(140, 275, 2):
    """
    for x in range(60,241,2):
    for y in range(60,241, 2):
    phase = initial_phase_orig( 257.-x, 257.-y, 512)
    #write2file(phase, 'x%3d_y%3d'%(x,y))
    print 'making %d, %d'%(x,y)
    write2file(phase, phasemap,SLMpath, 'x%d_y%d'%(x,y) )
    """
    err = 0
    for x in range(512):
        for y in range(512):
            phase1 = initial_phase_orig(x,y,512)
            phase2 = initial_phase_orig2(x,y,512)
            err += (phase1-phase2).sum() 
    print 'err', err
