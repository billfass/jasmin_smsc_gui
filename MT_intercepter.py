#!/usr/bin/env python

import json
import requests
import datetime

try:
    routable
    smpp_status = "ESME_ROK"
    http_status = 200
except Exception as e:
    smpp_status = "ESME_RCANCELFAIL"
    http_status = 400