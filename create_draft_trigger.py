#Author: R.Gayathri
#Date Created: July 2026


from pathlib import Path
from datetime import datetime
import sys

ROOT_FOLDER = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT_FOLDER))

from modules.status.status_manager import (
    update_status
)

TRIGGER_FILE = (
    ROOT_FOLDER
    / "config"
    / "draft_request.txt"
)

try:

    with open(
        TRIGGER_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )

    update_status(
        "Create Email Draft",
        "SUCCESS"
    )

    print(
        "Draft request triggered successfully."
    )

except Exception:

    update_status(
        "Create Email Draft",
        "FAILED"
    )

    raise