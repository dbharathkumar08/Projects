#!/usr/bin/python

import os, sys

os.system("kill -9 $(ps aux | grep python | grep " + sys.argv[1]  + " | awk '{print $2}')")