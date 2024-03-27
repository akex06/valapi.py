import requests
from requests.auth import HTTPBasicAuth
from valorant import LockFile

lockfile = LockFile()

print(requests.get(f"https://127.0.0.1:{lockfile.port}/rso-auth/v1/authorization/userinfo",
                   auth=HTTPBasicAuth("riot", lockfile.password), verify=False ).text)