#!/usr/bin/env python

import json
import requests
from datetime import datetime

EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID

def send_sms_via_api(from_, to, message, type_, dlr):
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
        if response.status_code == 200:
            return True, response.json()  # Réponse OK
        else:
            return False, response.text  # Réponse en erreur
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return False, str(e)
    
globals()['json'] = json
try:
    dateSend = datetime.now().isoformat() + 'Z'
    to = routable.pdu.params['destination_addr']
    sender = routable.pdu.params['source_addr']
    content = routable.pdu.params['short_message']
    message_type = 'text'  # Type de message (par défaut 'text')
    dlr = '1'  # DLR (par défaut 1 pour accusé de réception)

    # Envoi du SMS via l'API HTTP externe
    success, api_response = send_sms_via_api(sender, to, content, message_type, dlr)
except Exception as e:
    # We got an error when calling for charging
    # Return ESME_RDELIVERYFAILURE
    # smpp_status = 254
    http_status = 400
else:
    # CGRateS has returned a value

    if success:
        # Return ESME_ROK
        # smpp_status = 0
        http_status = 200
    else:
        # Return ESME_RDELIVERYFAILURE
        # smpp_status = 254
        http_status = 400
finally:
    log_file = "/var/log/jasmin/mt_interceptor.log"
    with open(log_file, "a") as file:
        file.write("{0} : send SMS from {1} to {2} ({3}-{4})".format(dateSend, sender, to, success, api_response))
        file.write('\n')