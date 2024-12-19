#!/usr/bin/env python

import json
import re

globals()['json'] = json
globals()['re'] = re
try:
    m_user = routable.user
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']
    log_file = "/var/log/jasmin/rouch_intercepter.log"

    api_text = json.dumps({"m_user": m_user, "to":to, "sender":sender, "message": "Send SMS"})

    with open(log_file, "a") as file:
        file.write("{0}".format(api_text))
        file.write('\n')

    # Définir le motif
    pattern = r"^229(01)?(55|58|6[03-58]|9[3-589])[0-9]{6}$"

    # Exemple de fonction pour valider
    def match_number(number):
        return bool(re.match(pattern, number))

    if m_user == "FAST_6924" :
        # Tester la fonction
        if match_number(to):
            raise Exception("Sending SMS LOCK")

    smpp_status = 0
except Exception as e:
    api_text = json.dumps({"m_user": m_user, "to":to, "sender":sender, "message": str(e)})
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    smpp_status = 254
finally:
    with open(log_file, "a") as file:
        file.write("{0}".format(api_text))
        file.write('\n')