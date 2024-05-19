import os
import subprocess
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator
from pydantic_core.core_schema import ValidationInfo

from mealie.schema._mealie.types import NoneFloat

from . import utils
from .pre_processor import pre_process_string

CWD = Path(__file__).parent
MODEL_PATH = os.getenv("CRF_MODEL_PATH", default=CWD / "model.crfmodel")


class CRFConfidence(BaseModel):
    average: float = 0.0
    comment: NoneFloat = None
    name: NoneFloat = None
    unit: NoneFloat = None
    qty: Annotated[NoneFloat, Field(validate_default=True)] = None


class CRFIngredient(BaseModel):
    input: str = ""
    name: str = ""
    other: str = ""
    qty: Annotated[str, Field(validate_default=True)] = ""
    comment: str = ""
    unit: str = ""
    confidence: CRFConfidence

    @field_validator("qty", mode="before")
    def validate_qty(cls, qty, info: ValidationInfo):
        if qty is not None and qty != "":
            return qty

        # Check if other contains a fraction
        try:
            if info.data["other"] is not None and info.data["other"].find("/") != -1:
                return str(round(float(Fraction(info.data["other"])), 3))
            else:
                return "0"
        except Exception:
            return ""


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
