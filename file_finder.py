
#Author: R.Gayathri
#Date Created: July 2026


from pathlib import Path


def get_item_list_file(run_folder):

    files = list(
        Path(run_folder).glob("*.xlsx")
    )

    if not files:

        raise FileNotFoundError(
            f"No Excel file found in {run_folder}"
        )

    return str(files[0])