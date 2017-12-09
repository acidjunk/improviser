# Copyright (c) 2010 stas zytkiewicz stas.zytkiewicz@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License
# as published by the Free Software Foundation.  A copy of this license should
# be included in the file GPL-3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# provides a logging object
# All modules get the same logger so this must called asap

import os
from conf import ConfParser

if os.path.exists('render.conf'):
    confpath = 'render.conf'
elif os.path.exists('render.dev'):
    confpath = 'render.dev'
else:
    module_logger.error("No conf file found")
    import sys
    sys.exit()

cfp = ConfParser(confpath)
logbase = "%s" % cfp.get_value("logs","logbasepath")
if not os.path.exists(logbase):
    os.makedirs(logbase)
LOGLEVEL = cfp.get_value("logs","level")
LOGPATH = os.path.join(logbase, 'render.log')

# remove old log
#if os.path.exists(LOGPATH):
#    try:
#        os.remove(LOGPATH)
#    except Exception, info:
#        print "Failed to remove old log"
#        print info
#    else:
#        print "removed old logpath"
        
# set loglevel, possible values:
# logging.DEBUG
# logging.INFO
# logging.WARNING
# logging.ERROR
# logging.CRITICAL
import logging, logging.handlers

lleveldict = {'debug':logging.DEBUG,
    'info':logging.INFO,
    'warning':logging.WARNING,
    'error':logging.ERROR,
    'critical':logging.CRITICAL}
if not lleveldict.has_key(LOGLEVEL):
    print "Invalid loglevel: %s, setting loglevel to 'debug'" % LOGLEVEL
    llevel = lleveldict['debug']
else:
    llevel = lleveldict[LOGLEVEL]
CONSOLELOGLEVEL = llevel
FILELOGLEVEL = llevel

def start():
    global CONSOLELOGLEVEL, FILELOGLEVEL
    #create logger
    logger = logging.getLogger("render")
    logger.setLevel(CONSOLELOGLEVEL)
    #create console handler and set level
    ch = logging.StreamHandler()
    ch.setLevel(CONSOLELOGLEVEL)
    #create file handler and set level
    fh = logging.FileHandler(LOGPATH)
    fh.setLevel(FILELOGLEVEL)
    #create formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    #add formatter to ch and fh
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    #add ch and fh to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.info("File logger created: %s" % LOGPATH)
    
    # test
    module_logger = logging.getLogger("render.myLogger")
    module_logger.info("logger created, start logging")
    
