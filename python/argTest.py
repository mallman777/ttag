# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 11:04:52 2015

@author: mallman
"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('Tacq', type  = float, help = 'Acquistion time in seconds')
parser.add_argument('-s', type = int, nargs = '+', help = 'decide if scan is used')
parser.add_argument('-f', type = int, nargs = 3, help = 'decide if f is used')
args = parser.parse_args()
if args.s:
    print "we are doing a scan"
    print type(args.s)
    print args.s

else:
    print args.Tacq
    print "We are not doing a scan"

if args.f:
    print args.f