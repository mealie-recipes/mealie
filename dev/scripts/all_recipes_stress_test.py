import json
import random
import string
import time

import requests


def random_string(length: int) -> str:
    return "".join(random.choice(string.ascii_lowercase) for _ in range(length))


def payload_factory() -> dict:
    return {"name": random_string(15)}


def login(username="changeme@email.com", password="MyPassword"):

    payload = {"username": username, "password": password}
    r = requests.post("http://localhost:9000/api/auth/token", payload)

    # Bearer
    token = json.loads(r.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}


def populate_data(token):
    for _ in range(300):
        payload = payload_factory()
        r = requests.post("http://localhost:9000/api/recipes", json=payload, headers=token)

        if r.status_code != 201:
            print(f"Error: {r.status_code}")
            print(r.text)
            exit()

        else:
            print(f"Created recipe: {payload}")


def time_request(url, headers):
    start = time.time()
    _ = requests.get(url, headers=headers)
    end = time.time()
    print(end - start)


def main():
    print("Starting...")
    token = login()
    # populate_data(token)

    for _ in range(10):
        time_request("http://localhost:9000/api/recipes", token)

    print("Finished...")


if __name__ == "__main__":
    main()
