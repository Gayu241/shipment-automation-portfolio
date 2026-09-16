from pathlib import Path

import pandas as pd


ROOT_FOLDER = Path(__file__).resolve().parents[2]

STATUS_FILE = (
    ROOT_FOLDER
    / "config"
    / "live_status.csv"
)


def update_status(step, status):

    df = pd.read_csv(
        STATUS_FILE
    )

    df.loc[
        df["Step"] == step,
        "Status"
    ] = status

    df.to_csv(
        STATUS_FILE,
        index=False
    )

    print(
        f"{step} : {status}"
    )