from py4web import action, request
from .common import db, session, auth, flash, jasmin, api_resp, api_id
from pydal.validators import *
from .utils import cols_split
from .filter_manager import list_filters
from .user_manager import list_groups, list_users
from .api_mtrouters import list_connectors, list_mtroutes

import json
import copy

def transform_filters(input_data, output_file="resultat.json"):
    """
    Transforme une liste de filtres (User, DestAddr, Group) vers le format standardisé.

    Args:
        input_data (list): Liste des dictionnaires source.
        output_file (str): Nom du fichier de sortie.

    Returns:
        list: La liste des données transformées.
    """
    type_mapping = {
        "UserFilter": {
            "key": "uid", 
            "fmt": "<U (uid={})>"
        },
        "DestinationAddrFilter": {
            "key": "destination_addr", 
            "fmt": "<DA (dst_addr={})>"
        },
        "GroupFilter": {
            "key": "gid", 
            "fmt": "<G (gid={})>"
        }
    }

    output_list = []

    for item in input_data:
        f_type = item.get("filter_type")
        raw_val = item.get("description")
        
        config = type_mapping.get(f_type, {"key": "value", "fmt": "<Val (v={})>"})
        
        new_obj = {
            "fid": item.get("filter_id"),
            "type": f_type,
            "routes": item.get("route", "").replace("/", " "),
            "description": config["fmt"].format(raw_val),
            "params": {
                config["key"]: raw_val
            }
        }
        output_list.append(new_obj)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Fichier généré : {output_file}")
    return output_list

def transform_groups(input_data, output_file="groups_result.json"):
    """
    Ajoute un statut d'activation par défaut à une liste de groupes (GID).

    Args:
        input_data (list): Liste de dictionnaires contenant la clé 'gid'.
        output_file (str): Nom du fichier JSON de sortie.

    Returns:
        list: La liste transformée avec la clé 'activated': True ajoutée.
    """
    output_list = [
        {
            "gid": item.get("gid"),
            "activated": True
        }
        for item in input_data
    ]

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Fichier généré : {output_file}")
    return output_list

def transform_user_creds(input_data, output_file="users_creds_result.json"):
    """
    Transforme une liste d'utilisateurs simples en une structure complexe de crédits/quotas.

    Args:
        input_data (list): Liste des dictionnaires utilisateurs sources (avec uid, gid, username, balanceh).
        output_file (str): Nom du fichier de sortie.

    Returns:
        list: La liste transformée avec la structure de configuration complète.
    """
    
    template = {
        "mt_messaging_cred": {
            "authorization": {
                "http_send": True, "http_balance": True, "http_rate": True,
                "http_bulk": False, "smpps_send": True, "http_long_content": True,
                "dlr_level": True, "http_dlr_method": True, "src_addr": True,
                "priority": True, "validity_period": True,
                "schedule_delivery_time": True, "hex_content": True
            },
            "valuefilter": {
                "dst_addr": ".*", "src_addr": ".*",
                "priority": "^[0-3]$", "validity_period": "^\\d+$", "content": ".*"
            },
            "defaultvalue": {"src_addr": None},
            "quota": {
                "balance": 0, 
                "early_percent": None, "sms_count": None,
                "http_throughput": None, "smpps_throughput": None
            }
        },
        "smpps_cred": {
            "authorization": {"bind": True},
            "quota": {"max_bindings": None}
        },
        "uid": "",       
        "gid": "",       
        "username": ""   
    }

    output_list = []

    for item in input_data:
        new_obj = copy.deepcopy(template)
        
        new_obj["uid"] = item.get("uid")
        new_obj["gid"] = item.get("gid")
        new_obj["username"] = item.get("username")

        raw_balance = str(item.get("balanceh", "0"))
        
        if "ND" in raw_balance or "(!)" in raw_balance:
            balance_val = 0
        else:
            try:
                balance_val = float(raw_balance)
            except ValueError:
                balance_val = 0

        new_obj["mt_messaging_cred"]["quota"]["balance"] = balance_val

        output_list.append(new_obj)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Fichier généré : {output_file}")
    return output_list

def transform_routes(input_data, output_file="routes_result.json"):
    """
    Transforme des routes statiques brutes en configuration de routing enrichie.

    Args:
        input_data (list): Liste des routes avec 'connectors', 'filters', 'rate', 'order'.
        output_file (str): Nom du fichier de sortie.

    Returns:
        list: La liste transformée avec les connecteurs formatés et les types convertis.
    """
    output_list = []

    for item in input_data:
        try:
            raw_rate = float(item.get("rate", 0))
            order_val = int(item.get("order", 0))
        except ValueError:
            raw_rate = 0.0
            order_val = 0

        formatted_connectors = [
            f"to smppc({c}) rated {raw_rate:.2f}" 
            for c in item.get("connectors", [])
        ]

        formatted_filters = []
        for f_name in item.get("filters", []):
            if "grp" in f_name:
                formatted_filters.append(f"<G (gid={f_name})>")
            elif f_name.isdigit() or f_name.startswith("^"):
                formatted_filters.append(f"<DA (dst_addr={f_name})>")
            else:
                formatted_filters.append(f"<FID (fid={f_name})>")

        new_obj = {
            "order": order_val,
            "type": item.get("type"),
            "connectors": formatted_connectors,
            "filters": formatted_filters,
            "rate": int(raw_rate) if raw_rate.is_integer() else raw_rate,
            "isRated": True
        }
        output_list.append(new_obj)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Fichier généré : {output_file}")
    return output_list

def transform_connectors(input_data, output_file="connectors_result.json"):
    """
    Transforme la configuration brute des connecteurs SMPP vers le format typé (Jasmin).

    Args:
        input_data (list): Liste des dictionnaires connecteurs bruts (tout en string).
        output_file (str): Nom du fichier de sortie.

    Returns:
        list: La liste transformée avec les bons types (int, bool, null).
    """
    
    def clean_str(val):
        """Retourne None si la chaine est 'None', sinon la valeur."""
        return None if str(val) == "None" else val

    def to_int(val):
        """Convertit en entier, gère le None."""
        val = clean_str(val)
        return int(val) if val is not None else None

    def to_bool(val):
        """Convertit 'yes'/'no' en True/False."""
        return str(val).lower() == "yes"

    output_list = []

    for item in input_data:
        new_obj = {
            "cid": item.get("cid"),
            "host": item.get("host"),
            "port": to_int(item.get("port")),
            "username": item.get("username"),
            "password": item.get("password"),
            "systype": clean_str(item.get("systype")), 
            
            "logfile": item.get("logfile"),
            "logrotate": item.get("logrotate"),
            "log_level": to_int(item.get("loglevel")), 
            "logprivacy": to_bool(item.get("logprivacy")),

            "bind_type": item.get("bind"), 
            "bind_to": to_int(item.get("bind_to")),
            "trx_to": to_int(item.get("trx_to")),
            "res_to": to_int(item.get("res_to")),
            "pdu_red_to": to_int(item.get("pdu_red_to")),
            "con_loss_retry": to_bool(item.get("con_loss_retry")),
            "con_loss_delay": to_int(item.get("con_loss_delay")),
            "con_fail_retry": to_bool(item.get("con_fail_retry")),
            "con_fail_delay": to_int(item.get("con_fail_delay")),
            "elink_interval": to_int(item.get("elink_interval")),
            "ssl": to_bool(item.get("ssl")),

            "bind_ton": to_int(item.get("bind_ton")),
            "bind_npi": to_int(item.get("bind_npi")),
            "src_ton": to_int(item.get("src_ton")),
            "src_npi": to_int(item.get("src_npi")),
            "dst_ton": to_int(item.get("dst_ton")),
            "dst_npi": to_int(item.get("dst_npi")),
            "addr_range": clean_str(item.get("addr_range")),
            "src_addr": clean_str(item.get("src_addr")),

            "proto_id": to_int(item.get("proto_id")), 
            "priority": to_int(item.get("priority")),
            "validity": clean_str(item.get("validity")),
            "ripf": to_int(item.get("ripf")),
            "def_msg_id": to_int(item.get("def_msg_id")),
            "coding": to_int(item.get("coding")),
            "requeue_delay": to_int(item.get("requeue_delay")),
            "submit_throughput": to_int(item.get("submit_throughput")),
            "dlr_expiry": to_int(item.get("dlr_expiry")),
            "dlr_msgid": to_int(item.get("dlr_msgid"))
        }
        output_list.append(new_obj)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_list, f, indent=2)
    
    print(f"Fichier généré : {output_file}")
    return output_list

@action('api/export/<action>', method=['GET', 'POST'])
@action.uses(db, session, auth, flash)
def export_manage(action=None):
    ret = api_id(request)
    if ret:
        return api_resp(dict(), 400, ret)
    
    data = request.POST

    try:
        if action == "groups":
            transform_groups(list_groups(), "static/groups.json")
        elif action == "users":
            transform_user_creds(list_users(), "static/users.json")
        elif action == "filters":
            transform_filters(list_filters(), "static/filters.json")
        elif action == "connectors":
            transform_connectors(list_connectors(), "static/smppconnectors.json")
        elif action == "mtroutes":
            transform_routes(list_mtroutes(), "static/mtroutes.json")
        else:
            return api_resp(dict(data), 400, 'Undefined action')
    except Exception as e:
        return api_resp(dict(request.POST), 400, str(e))

    return api_resp(dict(data), ret["code"], ret["message"])

