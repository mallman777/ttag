# -*- coding: utf-8 -*-
"""
Created on Sat May 10 21:56:39 2014

@author: nams
"""

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np
import time
import threading

class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)

    def adjustsize(self):
        font = self.font()
        text = self.text()
        newlines = text.count('\n')+1
        textheight = self.fontMetrics().boundingRect(text).height()
        fontsize = self.height()*0.8/newlines
        font.setPixelSize(fontsize)
        self.setFont(font)
        textwidth = self.fontMetrics().boundingRect(text).width()
        if textwidth > self.width():
            fontsize = 2.0 * self.width()/textwidth * fontsize
            font.setPixelSize(fontsize)
            self.setFont(font)
            textheight = self.fontMetrics().boundingRect(text).height()
            textwidth = self.fontMetrics().boundingRect(text).width()
        self.setFont(font)
    def resizeEvent(self, evt):
        self.adjustsize()        

if __name__ == '__main__':
  app = QtGui.QApplication([])
  label = StretchedLabel()
  #label.resize(300,150)
  label.setText('%.2f'%time.time())
  label.show()
  label.raise_()
  label2 = StretchedLabel()
  label2.setText('Hello\nWorld')
  label2.show()
  label2.raise_()
  #label.setText('Hello\nWorld')
  #label.show()
  """
  def update():
    global label
    if not label.isVisible():
      return
    threading.Timer(1,update).start()
    label.setText(time.ctime(time.time()))
    print label.isVisible()
    #label.show()
  #update() 
  """ 
  def update2():
    global label
    while label.isVisible():
      label.setText('%.2f'%time.time())
  thread1 = threading.Thread(None, update2)
  thread1.start()
  #update() 
  """
  # This doesn't work
  while label.isVisible():
    label.setText(time.ctime(time.time()))
    print 'looping'
    time.sleep(1)
  """    
  app.exec_()
  print 'got to end'
  #import sys
  #if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
  #  QtGui.QApplication.instance().exec_()


