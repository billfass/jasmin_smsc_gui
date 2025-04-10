import requests
import datetime

# Tu peux définir ici une correspondance username => password
USER_CREDENTIALS = {
    'Urban002': 'Urban002',
    'inte5564': 'd7a9763c',
    'supp7769': '42e2e514',
    'josa8235': '8964d378',
    #'user2': 'pass2',
    #'smppuser': 'smpppass',
    # Ajoute tous tes utilisateurs ici
}

today = datetime.datetime.now().strftime("%Y%m%d")
log_file = "/var/log/jasmin/intercepter_rsubmitfail_{0}.log".format(today)

text_log = "[Interceptor] reading..."
with open(log_file, "a") as file:
    file.write("{0}".format(text_log))
    file.write('\n')

def mt_interceptor_smpp(message):
    # Obtenir la date du jour
    text_log = "[Interceptor] {0} to {1}.".format(message.status, message.destination_addr)
    with open(log_file, "a") as file:
        file.write("{0}".format(text_log))
        file.write('\n')

    if message.status == 'ERROR/ESME_RSUBMITFAIL':
        text_log = "[Interceptor] ESME_RSUBMITFAIL - triggering resend."
        with open(log_file, "a") as file:
            file.write("{0}".format(text_log))
            file.write('\n')
    
        try:
            # Récupération des infos du message
            to = message.destination_addr
            sender = message.source_addr
            content = message.short_message.decode('utf-8')
            username = message.user.username
            password = USER_CREDENTIALS.get(username)
            dlr_url = getattr(message, 'dlr_url', None)

            if not password:
                message.log.error("[Interceptor] No password found for user: , skipping resend.")
                return message

            # Requête vers /send
            data = {
                "username": username,
                "password": password,
                "to": to,
                "from": sender,
                "text": content,
                "messageId": message.message_id,
                "resend": "true"
            }
            
            if dlr_url:
                data["dlr-url"] = dlr_url
        
            response = requests.post(
                "https://api.fastermessage.com/sms/send",
                data=data,
                timeout=5
            )
            message.log.info("[Interceptor] Resend done: ")
        except Exception as e:
            message.log.error("[Interceptor] Resend failed:")

        message.retry = False  # On évite que Jasmin retry lui-même

    return message
