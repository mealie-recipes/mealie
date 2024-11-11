import os
import sys

import requests


def main():
    port = os.getenv("API_PORT")

    if port is None:
        port = 9000

    if all(os.getenv(x) for x in ["TLS_CERTIFICATE_PATH", "TLS_PRIVATE_KEY_PATH"]):
        proto = "https"
    else:
        proto = "http"

    url = f"{proto}://127.0.0.1:{port}/api/app/about"

    # TLS certificate is likely not issued for 127.0.0.1 so don't verify
    r = requests.get(url, verify=False)

    if r.status_code == 200:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
