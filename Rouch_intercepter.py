#!/usr/bin/env python

import json
from datetime import datetime

globals()['json'] = json
try:
    message_user = routable.user
    daySend = datetime.now().strftime('%Y%m%d%H')
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    if message_user == "FAST_6924" :
        raise Exception("Fail sending SMS")

    message_user = routable.user

    smpp_status = 0
except Exception as e:
    # api_text = str(e)
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    smpp_status = 254
finally:
    log_file = "/var/log/jasmin/mt_interceptor/rouch_interceptor.log"