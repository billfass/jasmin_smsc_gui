#!/usr/bin/env python

import json
import requests
from datetime import datetime

EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID

def send_sms_via_api(from_, to, message, type_, dlr, url):
    return False, "Text réception", 410
    """Envoie le SMS via l'API externe."""
    try:
        sms_data = {
            'from': from_,
            'to': to,
            'type': type_,
            'message': message,
            'dlr': dlr
        }

        headers = {
            "APIKEY": API_KEY,
            "CLIENTID": CLIENT_ID
        }

        # Envoi du SMS via l'API
        response = requests.post(EXTERNAL_API_URL, data=sms_data, headers=headers)

        # Vérification du statut de la réponse
        if response.status_code > 199 and response.status_code < 300:
            return True, response.text  # Réponse OK
        else:
            return False, response.text  # Réponse en erreur
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return False, str(e)

globals()['json'] = json
globals()['requests'] = requests
globals()['EXTERNAL_API_URL'] = EXTERNAL_API_URL
globals()['API_KEY'] = API_KEY
globals()['CLIENT_ID'] = CLIENT_ID
try:
    dateSend = datetime.now().isoformat() + 'Z'
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']
    type = 0  # Type de message (par défaut 0 : 'text', 1 : 'Flash')
    dlr = 0  # DLR (par défaut 1 pour accusé de réception)
    url = ''  # DLR URL

    # Envoi du SMS via l'API HTTP externe
    success, api_response, api_code = send_sms_via_api(sender, to, content, type, dlr, url)

    if success == False:
        raise Exception(api_response)
except Exception as e:
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    # smpp_status = 254
    http_status = 400
finally:
    log_file = "/var/log/jasmin/mt_interceptor.log"
    with open(log_file, "a") as file:
        file.write("{0} : send SMS from {1} to {2} ({3} - {4})".format(dateSend, sender, to, success, api_response))
        file.write('\n')