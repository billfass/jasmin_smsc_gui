#!/usr/bin/env python

import json
import datetime

# Obtenir la date du jour
today = datetime.datetime.now().strftime("%Y%m%d")

log_file = "/var/log/jasmin/intercepter_sid_fastermsg"
try:
    user = 'UNKNOW' #routable.user.cid
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    if sender == 'FASTERMSG':
        routable.pdu.params['source_addr'] = 'OTPCode'
        raise Exception("SID FASTERMSG getting")
except Exception as e:
    api_text = json.dumps({"m_user": user, "to":to, "sender":sender, "message": str(e), "time": datetime.datetime.now().strftime("%Y%m%d%H%i%s")})
    # We got an error when calling for charging
    with open("{0}_{1}.log".format(log_file, today), "a") as file:
        file.write("{0}".format(api_text))
        file.write('\n')
#finally: