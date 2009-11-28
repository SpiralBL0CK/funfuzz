#!/usr/bin/env python

import os, sys, platform, signal
ready = False

def amiss(knownPath, crashLogFilename, verbose, msg):
    global ignoreList
    
    if not ready:
        readIgnoreList(knownPath)

    igmatch = []
    
    if os.path.exists(crashLogFilename):
        currentFile = file(crashLogFilename, "r")
        for line in currentFile:
            for ig in ignoreList:
                if line.find(ig) != -1:
                    igmatch.append(ig)
        currentFile.close()
        
        if len(igmatch) == 0:
            # Would be great to print [@ nsFoo::Bar] in addition to the filename, but
            # that would require understanding the crash log format much better than
            # this script currently does.
            print "Unknown crash: " + crashLogFilename
            return True
        else:
            if verbose:
                print "@ Known crash: " + ", ".join(igmatch)
            return False
    else:
        if platform.mac_ver()[0].startswith("10.4") and msg.find("SIGABRT") != -1:
            # Tiger doesn't create crash logs for aborts.  No cause for alarm.
            return False
        else:
            print "Unknown crash (crash log is missing)"
            return True


def readIgnoreList(knownPath):
    global ignoreList
    global ready
    ignoreList = []
    ignoreFile = file(os.path.join(knownPath, "crashes.txt"), "r")
    for line in ignoreFile:
        line = line.strip()
        if ((len(line) > 0) and not line.startswith("#")):
            ignoreList.append(line)
    ignoreFile.close()
    ready = True
    #print "detect_interesting_crashes is ready (ignoring %d strings)" % (len(ignoreList))


def ignore(assertion):
    global ignoreList
    for ig in ignoreList:
        if assertion.find(ig) != -1:
            return True
    return False
