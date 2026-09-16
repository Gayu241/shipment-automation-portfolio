from datetime import datetime
from pathlib import Path


ROOT_FOLDER = Path(__file__).resolve().parents[2]

LOG_FILE = (
    ROOT_FOLDER
    / "config"
    / "processed_shipments.txt"
)

def get_successful_shipments():

    successful = set()

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                parts = (
                    line.strip()
                    .split("|")
                )

                if (
                    len(parts) >= 2
                    and parts[1] == "SUCCESS"
                ):

                    successful.add(
                        parts[0]
                    )

    except FileNotFoundError:

        pass

    return successful


def log_success(
    shipment_no
):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{shipment_no}"
            f"|SUCCESS|"
            f"{datetime.now()}\n"
        )


def log_failed(
    shipment_no,
    error
):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{shipment_no}"
            f"|FAILED|"
            f"{datetime.now()}|"
            f"{error}\n"
        )