from fastapi import HTTPException
import json

with open('/home/equipo/MyProject/BckEnd/fast-api-project/secrets.json') as secrets_file:
    secrets = json.load(secrets_file)

def get_secret(setting, secrets=secrets):
    """Get secret setting or fail with ImproperlyConfigured"""
    try:
        return secrets[setting]
    except KeyError:
        print(f"Set the {setting} setting")
