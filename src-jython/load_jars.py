# -*- coding: utf-8 -*-
import os
import sys
from java import io, net, lang

def loadJar(jarFile):
    '''load a jar at runtime using the system Classloader (needed for JDBC)'''
    u = io.File(jarFile).toURL() if type(jarFile) != net.URL else jarFile
    m = net.URLClassLoader.getDeclaredMethod('addURL', [net.URL])
    m.accessible = 1
    print("%s" % lang.ClassLoader.getSystemClassLoader())
    m.invoke(lang.ClassLoader.getSystemClassLoader(), [u])

def loadsqldrivers():
    JARS_FILE_PATH = os.path.join(os.getcwd(),"src-jython", "jars")
    JARS_LIST = [file for file in os.listdir(JARS_FILE_PATH) if os.path.isfile(os.path.join(JARS_FILE_PATH, file)) and os.path.splitext(file)[1] == '.jar']
    for jar in JARS_LIST:
        jar_path = os.path.join(JARS_FILE_PATH, jar)
        if jar_path not in sys.path:
            loadJar(os.path.join(JARS_FILE_PATH, jar))
            