#!/usr/bin/env python

import json
import re
import datetime

globals()['re'] = re
try:
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    # Obtenir la date du jour
    today = datetime.datetime.now().strftime("%Y%m%d")
    totime = datetime.datetime.now().strftime("%Y%m%d%H")

    log_file = "/var/log/jasmin/intercepter_chen"

    # Exemple de fonction pour valider
    def match_number(number):
        return bool(re.match(r"^229(01)?(45||55|58|6[03-58]|9[3-589])[0-9]{6}$", number))

    # Tester la fonction
    if match_number(to):
        raise Exception("Sending SMS LOCK")

    # smpp_status = 0
except Exception as e:
    api_text = json.dumps({"to":to, "sender":sender, "message": str(e), "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    # We got an error when calling for charging
    with open("{0}_{1}.log".format(log_file, totime), "a") as file:
        file.write("{0}".format(api_text))
        file.write('\n')
    # Return ESME_RDELIVERYFAILURE
    http_status = 403
    smpp_status = 254
#finally: