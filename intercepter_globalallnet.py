#!/usr/bin/env python

import json
import re
import os
import datetime

globals()['re'] = re
try:
    m_user = "FAST_2157" # routable.user
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']

    # Obtenir la date du jour
    today = datetime.datetime.now().strftime("%Y%m%d")
    totime = datetime.datetime.now().strftime("%Y%m%d%H")

    if not os.path.exists("/var/log/jasmin/globalallnet_intercepter/"):
        os.makedirs("/var/log/jasmin/globalallnet_intercepter/", exist_ok=True)
    # Construire dynamiquement le chemin du fichier de log
    log_directory = "/var/log/jasmin/globalallnet_intercepter/20250307" #os.path.join("/var/log/jasmin/globalallnet_intercepter", today)
    # Créer le répertoire si nécessaire
    if not os.path.exists(log_directory):
        os.makedirs(log_directory, exist_ok=True)
    
    log_file = os.path.join(log_directory, totime, ".log")

    api_text = json.dumps({"m_user": m_user, "to":to, "sender":sender, "message": "Send SMS"})

    # Exemple de fonction pour valider
    def match_number(number):
        return bool(re.match(r"^229(01)?(55|58|6[03-58]|9[3-589])[0-9]{6}$", number))

    # Tester la fonction
    if match_number(to):
        raise Exception("Sending SMS LOCK")

    # smpp_status = 0
except Exception as e:
    api_text = json.dumps({"m_user": m_user, "to":to, "sender":sender, "message": str(e)})
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    http_status = 403
    smpp_status = 254
finally:
    with open(log_file, "a") as file:
        file.write("{0}".format(api_text))
        file.write('\n')