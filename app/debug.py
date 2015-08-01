#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from flask_blog import app

if len(sys.argv) >= 2:
    port = sys.argv[1]
else:
    port = '5005'

if len(sys.argv) >= 3:
    pidfile = sys.argv[2]
else:
    pidfile = os.path.join(os.path.dirname(__file__), 'flask.pid')

with open(pidfile, 'w') as fh:
    fh.write(str(os.getpid()))

app.run(debug=True, port=int(port))

# vim:set ft=python sw=4 et spell spelllang=en:
