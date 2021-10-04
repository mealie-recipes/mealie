import json
from pathlib import Path

import requests

CWD = Path(__file__).parent


def login(username="changeme@email.com", password="MyPassword"):

    payload = {"username": username, "password": password}
    r = requests.post("http://localhost:9000/api/auth/token", payload)

    # Bearer
    token = json.loads(r.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}


def main():
    print("Starting...")

    print("Finished...")


if __name__ == "__main__":
    main()
