# LOGGING
import logging

currentLogger = None

def initLogger(levelString):
    global currentLogger

    if levelString == 'DEBUG':
        logLevel = logging.DEBUG
    elif levelString == 'INFO':
        logLevel = logging.INFO
    elif levelString == 'WARNING':
        logLevel = logging.WARNING
    elif levelString == 'ERROR':
        logLevel = logging.ERROR
    else:
        logLevel = logging.DEBUG

    currentLogger = logging.getLogger('transform')
    currentLogger.setLevel(logLevel)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(logLevel)
    ch.setFormatter(formatter)
    currentLogger.addHandler(ch)
    return currentLogger