import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path

from pydantic import BaseModel, validator

from . import utils
from .pre_processor import pre_process_string

CWD = Path(__file__).parent
MODEL_PATH = CWD / "model.crfmodel"


class CRFConfidence(BaseModel):
    average: float = 0.0
    comment: float = None
    name: float = None
    unit: float = None
    qty: float = None


class CRFIngredient(BaseModel):
    input: str = ""
    name: str = ""
    other: str = ""
    qty: str = ""
    comment: str = ""
    unit: str = ""
    confidence: CRFConfidence

    @validator("qty", always=True, pre=True)
    def validate_qty(qty, values):  # sourcery skip: merge-nested-ifs
        if qty is None or qty == "":
            # Check if other contains a fraction
            try:
                if values["other"] is not None and values["other"].find("/") != -1:
                    return float(Fraction(values["other"])).__round__(1)
                else:
                    return 1
            except Exception:
                pass

        return qty


def _exec_crf_test(input_text):
    with tempfile.NamedTemporaryFile(mode="w") as input_file:
        input_file.write(utils.export_data(input_text))
        input_file.flush()
        return subprocess.check_output(["crf_test", "--verbose=1", "--model", MODEL_PATH, input_file.name]).decode(
            "utf-8"
        )


def convert_list_to_crf_model(list_of_ingrdeint_text: list[str]):
    crf_output = _exec_crf_test([pre_process_string(x) for x in list_of_ingrdeint_text])
    return [CRFIngredient(**ingredient) for ingredient in utils.import_data(crf_output.split("\n"))]
