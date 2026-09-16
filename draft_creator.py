#Author: R.Gayathri
#Date Created: July 2026


from pathlib import Path
import shutil
import sys

ROOT_FOLDER = Path(__file__).resolve().parents[2]

sys.path.insert(0, str(ROOT_FOLDER))

import pandas as pd

from modules.status.status_manager import (
    update_status
)

LOG_FILE = (
    ROOT_FOLDER
    / "config"
    / "prepared_files.txt"
)

EMAIL_FOLDER = (
    ROOT_FOLDER
    / "output_to_email"
)

EMAIL_SETTINGS_FILE = (
    ROOT_FOLDER
    / "config"
    / "email_settings.xlsx"
)

EMAIL_SUBJECT_FILE = (
    ROOT_FOLDER
    / "config"
    / "email_templates"
    / "email_subject.txt"
)

EMAIL_BODY_FILE = (
    ROOT_FOLDER
    / "config"
    / "email_templates"
    / "email_body.html"
)


def generate_email_template():

    print("\nGenerating Email Template...")

    EMAIL_SUBJECT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df = pd.read_excel(
        EMAIL_SETTINGS_FILE,
        sheet_name="EmailSettings",
        engine="openpyxl",
        header=None
    )

    subject = str(
        df.iloc[4, 1]
    ).strip()

    body_rows = []

    for row in range(7, 14):

        field_name = str(
            df.iloc[row, 1]
        ).strip()

        if (
            not field_name
            or field_name.lower() == "nan"
        ):
            continue

        body_rows.append(
            f"""
            <tr>
                <td>{field_name}</td>
                <td>&nbsp;</td>
            </tr>
            """
        )

    html_body = f"""
    <p>Hi All,</p>

    <p>FYI</p>

    <table border="1"
           cellpadding="5"
           cellspacing="0"
           style="border-collapse:collapse;">

        {''.join(body_rows)}

    </table>
    """

    with open(
        EMAIL_SUBJECT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(subject)

    with open(
        EMAIL_BODY_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(html_body)


def get_prepared_files():

    prepared = set()

    try:

        with open(
            LOG_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            for line in file:

                prepared.add(
                    line.strip()
                )

    except FileNotFoundError:

        pass

    return prepared


def mark_as_prepared(file_name):

    with open(
        LOG_FILE,
        "a",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{file_name}\n"
        )


def get_new_output_files():

    output_root = (
        ROOT_FOLDER
        / "output"
    )

    prepared = get_prepared_files()

    new_files = []

    for file in output_root.glob(
        "I*/*.xlsx"
    ):

        if file.name.upper() in {
            "T8_PO.XLSX",
            "LABEL_STATUS.XLSX"
        }:
            continue

        if file.name in prepared:

            print(
                f"Already Prepared : {file.name}"
            )

            continue

        print(
            f"New File Found : {file.name}"
        )

        new_files.append(file)

    return new_files


def create_email_draft():

    try:

        update_status(
            "Create Email Draft",
            "RUNNING"
        )

        print(
            "\nPREPARING EMAIL FILES..."
        )

        generate_email_template()

        files = get_new_output_files()

        if not files:

            print(
                "No new output files found."
            )

            update_status(
                "Create Email Draft",
                "NOT RUN"
            )

            return False

        EMAIL_FOLDER.mkdir(
            exist_ok=True
        )

        copied_count = 0

        for file in files:

            destination = (
                EMAIL_FOLDER
                / file.name
            )

            if destination.exists():

                print(
                    f"Already Exists : {file.name}"
                )

                continue

            shutil.copy2(
                file,
                destination
            )

            mark_as_prepared(
                file.name
            )

            copied_count += 1

            print(
                f"Copied : {file.name}"
            )

        if copied_count > 0:

            print(
                f"\n{copied_count} file(s) copied to output_to_email."
            )

            print(
                "Please verify sensitivity labels before creating the draft."
            )

            update_status(
                "Create Email Draft",
                "SUCCESS"
            )

            return True

        update_status(
            "Create Email Draft",
            "NOT RUN"
        )

        return False

    except Exception:

        update_status(
            "Create Email Draft",
            "FAILED"
        )

        raise


if __name__ == "__main__":

    create_email_draft()