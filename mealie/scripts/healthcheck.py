import os

import requests


def main():
    port = os.getenv("API_PORT")

    if port is None:
        port = 9000

    url = f"http://127.0.0.1:{port}/api/app/about"

    r = requests.get(url)

    if r.status_code == 200:
        exit(0)
    else:
        exit(1)


if __name__ == "__main__":
    main()
