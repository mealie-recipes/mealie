import requests

from mealie.services.parser_services import crfpp

MODEL_URL = "https://github.com/mealie-recipes/nlp-model/releases/download/v1.0.0/model.crfmodel"


def main():
    """
    Install the model into the crfpp directory
    """

    r = requests.get(MODEL_URL, stream=True, allow_redirects=True)
    with open(crfpp.MODEL_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


if __name__ == "__main__":
    main()
