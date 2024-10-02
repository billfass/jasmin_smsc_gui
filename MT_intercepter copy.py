#!/usr/bin/env python

import sys
import json
import requests
import datetime
import time

"""
keys_to_retrieve = [
    'priority_flag', 'source_addr', 'protocol_id', 'registered_delivery',
    'replace_if_present_flag', 'dest_addr_ton', 'source_addr_npi',
    'schedule_delivery_time', 'dest_addr_npi', 'esm_class', 'data_coding',
    'service_type', 'source_addr_ton', 'sm_default_msg_id', 'validity_period',
    'destination_addr', 'short_message'
]

write_log(routable.pdu.params["data_coding"])
write_log(routable.pdu.params["source_addr"])
write_log(routable.pdu.params["destination_addr"])
write_log(routable.pdu.params["short_message"])
write_log(routable.pdu.params["protocol_id"])
write_log(routable.pdu.params["registered_delivery"])
write_log(routable.pdu.params["service_type"])
write_log(routable.pdu.params["sm_default_msg_id"])
"""

# API HTTP externe (URL et API Key)
EXTERNAL_API_URL = "https://edok-api.kingsmspro.com/api/v1/sms/send"
API_KEY = 'NgDnKzjDpv3EndwGiOrVBBLHDivERcZt'  # clé API
CLIENT_ID = "2839"  #  client ID
NOW = datetime.datetime.now()
NOW_TIME = time.mktime(NOW.timetuple())
#Rejeter le message par défaut
smpp_status = "ESME_RCANCELFAIL"
http_status = 400


def write_log(message):
    log_file = "/var/log/jasmin/mt_interceptor.log"
    with open(log_file, "a") as file:
        file.write("{0}".format(message))
        file.write('\n')

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
            #sys.stderr.write(f"Erreur d'envoi : {response.status_code} - {response.text}\n")
            return False, response.text  # Réponse en erreur
    except Exception as e:
        #sys.stderr.write(f"Erreur d'envoi de l'API : {str(e)}\n")
        return False, str(e)

def intercept_sms(message):
    """Intercepte et traite le message SMS."""
    try:
        # Récupération des informations du message intercepté (Jasmin envoie les données via stdin)
        message_data = json.loads(message)

        to = message_data['to']
        sender = message_data['from']
        content = message_data['content']
        message_type = message_data.get('type', 'text')  # Type de message (par défaut 'text')
        dlr = message_data.get('dlr', '1')  # DLR (par défaut 1 pour accusé de réception)

        # Envoi du SMS via l'API HTTP externe
        success, api_response = send_sms_via_api(sender, to, content, message_type, dlr)

        if success:
            return True, "Message envoyé avec succès via l'API. {api_response}\n"
        else:
            #sys.stderr.write(f"Échec de l'envoi via l'API : {api_response}\n")
            return False, api_response  # Échec de l'envoi

    except Exception as e:
        #sys.stderr.write(f"Erreur : {str(e)}\n")
        return False, str(e)

#if __name__ == "__main__":
# Lire le message depuis stdin (transmis par Jasmin)
#message = json.dumps(sys.stdin.read().split())
message = json.dumps(routable)

# Log du message
write_log("")
write_log(NOW)
write_log(NOW_TIME)
write_log(message)

# Appeler la fonction pour traiter le message
success, result = intercept_sms(message)

if success:
    write_log(NOW_TIME)
    write_log(json.dumps({"status": 200, "message": result}))
    sys.stdout.write(json.dumps({"status": 200, "message": result}))
else:
    write_log(NOW_TIME)
    write_log(json.dumps({"status": 500, "message": result}))
    sys.stdout.write(json.dumps({"status": 500, "message": result}))
