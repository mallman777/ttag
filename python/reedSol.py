# -*- coding: utf-8 -*-
"""
Created on Mon Mar  2 12:48:37 2015

@author: qittlab
"""

import numpy as np
import scipy as sp

def getProb(n,p,t):
    prob = (sp.factorial(n)/(sp.factorial(t)*sp.factorial(n-t)))*(1-p)**t*p**(n-t) + p**n
    return prob
    
if __name__ == '__main__':
    n = 10
    p = 0.8
    t = 1
    print getProb(n,p,t)