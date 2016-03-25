#!/usr/bin/env python
# -*- coding:utf-8 -*-

import logging
import os,os.path
import datetime

_filefmt=os.path.join("logs","%Y-%m-%d","%Y-%m-%d.log")
class WangliLoggerHandler(logging.Handler):
    def __init__(self,filefmt=None):
        self.filefmt=filefmt
        if filefmt is None:
            self.filefmt=_filefmt
        logging.Handler.__init__(self)
    def emit(self,record):
        msg=self.format(record)
        _filePath=datetime.datetime.now().strftime(self.filefmt)
        _dir=os.path.dirname(_filePath)
        try:
            if os.path.exists(_dir) is False:
                os.makedirs(_dir)
        except Exception:
            print "can not make dirs"
            print "filepath is "+_filePath
            pass
        try:
            _fobj=open(_filePath,'a') 
            _fobj.write(msg)
            _fobj.write("\n")
            _fobj.flush()
            _fobj.close()
        except Exception:
            print "can not write to file"
            print "filepath is "+_filePath
            pass