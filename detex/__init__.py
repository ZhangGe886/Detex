# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#   Author: Derrick Chambers
# ------------------------------------------------------------------------------
"""
deTex: A Python Toolbox for running subspace detections.
==================================================================
"""
# python 2 and 3 compatibility imports
from __future__ import division
from __future__ import print_function, absolute_import, unicode_literals

# General imports
import os
import inspect
import logging
import logging.handlers
import sys

# Detex imports
import detex
import detex.getdata
import detex.util
import detex.subspace
import detex.fas
import detex.construct
import detex.results
import detex.streamPick
import detex.pandas_dbms
import detex.detect

# import warnings

logging.basicConfig()

# import all modules in detex directory
# modules = glob.glob(os.path.dirname(__file__)+"/*.py")
# __all__ = [os.path.basename(f)[:-3] for f in modules if os.path.isfile(f)]
# warnings.filterwarnings('error') #uncomment this to make all warnings errors

# Imports for lazy people (ie make detex.createCluster callable)
from detex.construct import createCluster, createSubSpace
from detex.util import loadClusters, loadSubSpace

# load clusters
version = os.path.join(os.path.dirname(detex.__file__), 'version.py')
with open(version) as vfil:
    __version__ = vfil.read().strip()
# detResults=results.detResults

maxSize = 10 * 1024 * 1024  # max size log file can be in bytes (10 mb defualt)
verbose = True  # set to false to avoid printing to screen
makeLog = False  # set to false to not make log file


## Configure logger to be used across all of Detex
def setLogger(fileName='detex_log.log', deleteOld=False):
    """
    Function to set up the logger used across Detex

    Parameters
    ----------
    fileName : str
        Path to log file to be created
    deleteOld : bool
        If True, delete any file of fileName if exists
    """
    reload(logging)  # reload to reconfigure default ipython log
    # set makeLog to True
    global makeLog
    makeLog = True
    cwd = os.getcwd()
    fil = os.path.join(cwd, fileName)
    if os.path.exists(fil):
        if os.path.getsize(fil) > maxSize:
            print('old log file %s exceeds size limit, deleting' % fil)
            os.remove(fil)
        elif deleteOld:
            os.path.realpath(fil)
    fh = logging.FileHandler(fil)
    fh.setLevel(logging.DEBUG)
    fmat = '%(asctime)s\t%(name)s\t%(levelname)s\t%(message)s'
    formatter = logging.Formatter(fmat)
    fh.setFormatter(formatter)
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(fh)
    lpath = os.path.abspath(fileName)
    logger.info('Starting logging, path to log file: %s' % fil)


# define basic logging function

def log(name, msg, level='info', pri=False, close=False, e=None):
    """
    Function to log important events as detex runs
    Parameters
    ----------
    name : the __name__ statement
        should always be set to __name__ from the log call. This will enable
        inspect to trace back to where the call initially came from and
        record it in the log
    msg : str
        A message to log
    level : str
        level of event (info, debug, warning, critical, or error)
    pri : bool
        If true print msg to screen without entire log info
    close : bool
        If true close the logger so the log file can be opened
    e : Exception class or None
        If level == "error" and Exception is raised, e is the type of
        exception
    """

    if not verbose:
        pri = False

    # get name of function that called log
    cfun = inspect.getouterframes(inspect.currentframe())[1][0].f_code.co_name
    log = logging.getLogger(name + '.' + cfun)
    if level == 'info' and makeLog:
        log.info(msg)
    elif level == 'debug' and makeLog:
        log.debug(msg)
    elif (level == 'warning' or level == 'warn') and makeLog:
        log.warning(msg)
    elif level == 'critical' and makeLog:
        log.critical(msg)
    elif level == 'error' or e is not None:
        if makeLog:
            log.error(msg)
        if makeLog:
            closeLogger()
        if e is None:
            e = Exception
        raise e(msg)
    else:
        if makeLog:
            raise Exception('level input not understood, acceptable values are'
                            ' "debug","info","warning","error","critical"')
    if pri:
        print(msg)
    if close and makeLog:  # close logger
        closeLogger()


def closeLogger():
    handlers = logger.handlers[:]
    for handler in handlers:
        handler.close()
        logger.removeHandler(handler)


if makeLog:
    setLogger()
