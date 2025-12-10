import json
import requests

with open("key.json", "r") as f:
    config = json.load(f)

def get_token_magento():
    url = f"{config['magento_url']}/rest/default/V1/integration/admin/token"
    payload = {
        "username": config["username_magento"],
        "password": config["password_magento"]
    }

    response = requests.post(url, json=payload, verify=False)
    if response.status_code != 200:
        raise Exception("Login failed")
    return response.json()

def get_token_medusa():
    url = f"{config['medusa_url']}/auth/user/emailpass"
    payload = {
        "email": config["email_medusa"],
        "password": config["password_medusa"]
    }

    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise Exception("Login failed")
    return response.json()