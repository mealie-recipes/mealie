from pathlib import Path

from mealie import __version__

APP_VERSION = __version__

CWD = Path(__file__).parent
BASE_DIR = CWD.parent.parent.parent
