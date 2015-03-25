# -*- coding: utf-8 -*-
"""
Created on Mon Mar 09 17:48:25 2015

@author: mallman
"""
import gen_find_nano_patterns as gp
import numpy as np

phaseMap = np.loadtxt('slm3381_at635_DVI.txt', dtype = np.uint32)
interpSettings = gp.getInterpSettings()
origPath = "/mnt/SLM/Dan/OptimizeSLM/Patterns/OrigSettings/"
nrows = 512
for i in range(64):
  print i, interpSettings[i,0],interpSettings[i,1]
#  p = gp.initial_phase_orig(257-interpSettings[i,0], 257-interpSettings[i,1],nrows)
#  gp.write2file(p, gp.phasemap, origPath, "%d"%i)
  #p = gp.initial_phase(interpSettings[i,0], interpSettings[i,1],nrows)
  #gp.write2file(p, phaseMap, origPath, "%d"%i)
