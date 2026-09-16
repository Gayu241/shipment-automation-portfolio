from pathlib import Path
from datetime import timedelta

import pandas as pd
from openpyxl import load_workbook


def update_label_status():

    root = Path.cwd()

    output_folder = root / "output"

    config_file = (
        root / "config" / "進退貨明細表.xlsx"
    )

    label_status_folder = (
        output_folder / "Label Status"
    )

    label_status_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    ignore_folders = {
        "EDC",
        "GDC",
        "T8 PO",
        "Label Status"
    }

    shipment_folders = [
        folder
        for folder in output_folder.iterdir()
        if (
            folder.is_dir()
            and folder.name not in ignore_folders
            and folder.name.startswith("I")
        )
    ]

    for shipment_folder in shipment_folders:

        invoice_no = shipment_folder.name

        print(
            f"\nProcessing Invoice : {invoice_no}"
        )

        try:

            shipment_file = (
                shipment_folder
                / f"{invoice_no}.xlsx"
            )

            if not shipment_file.exists():

                print(
                    f"Excel file not found : {shipment_file.name}"
                )

                continue

            month_code = (
                "20"
                + invoice_no[1:3]
                + invoice_no[3:5]
            )

            label_status_file = (
                label_status_folder
                / f"Label Status {month_code}.xlsx"
            )

            chinese_sheet = month_code

            try:

                chinese_df = pd.read_excel(
                    config_file,
                    sheet_name=chinese_sheet,
                    engine="openpyxl"
                )

            except Exception:

                print(
                    f"Chinese sheet not found : {month_code}"
                )

                continue

            invoice_lookup = {}

            for _, row in chinese_df.iterrows():

                invoice = str(
                    row.iloc[0]
                ).strip()

                inbound_date = row.iloc[5]

                invoice_lookup[
                    invoice
                ] = inbound_date

            # =====================================
            # READ SHIPMENT FILE LIKE SIOP TOOL
            # =====================================

            workbook = load_workbook(
                shipment_file,
                data_only=True
            )

            sheet = workbook.active

            data = list(
                sheet.values
            )

            shipment_df = pd.DataFrame(
                data
            )

            shipment_df.columns = (
                shipment_df.iloc[3]
            )

            shipment_df = shipment_df[4:]

            shipment_df.reset_index(
                drop=True,
                inplace=True
            )

            print(
                f"Columns Found : {list(shipment_df.columns)}"
            )

            item_col = None

            for col in shipment_df.columns:

                col_clean = (
                    str(col)
                    .strip()
                    .lower()
                )

                if col_clean in [
                    "item num",
                    "item number",
                    "itemnumber"
                ]:

                    item_col = col
                    break

            qty_col = None

            for col in shipment_df.columns:

                if (
                    str(col)
                    .strip()
                    .lower()
                    == "qty"
                ):

                    qty_col = col
                    break

            if item_col is None:

                print(
                    f"Item column not found in {shipment_file.name}"
                )

                continue

            if qty_col is None:

                print(
                    f"Qty column not found in {shipment_file.name}"
                )

                continue

            if label_status_file.exists():

                tracker_df = pd.read_excel(
                    label_status_file,
                    engine="openpyxl"
                )

            else:

                tracker_df = pd.DataFrame(
                    columns=[
                        "Invoice#",
                        "ITEM #",
                        "QTY",
                        "Inbound Date",
                        "Est. Finish Date"
                    ]
                )

            existing_keys = {}

            for idx, row in tracker_df.iterrows():

                key = (
                    f"{str(row['Invoice#']).strip()}|"
                    f"{str(row['ITEM #']).strip()}"
                )

                existing_keys[key] = idx

            rows_added = 0
            rows_updated = 0
            rows_skipped = 0

            for _, row in shipment_df.iterrows():

                item_no = str(
                    row[item_col]
                ).strip()

                qty = row[qty_col]

                key = (
                    f"{invoice_no}|{item_no}"
                )

                inbound_date = (
                    invoice_lookup.get(
                        invoice_no
                    )
                )

                est_finish_date = None

                if pd.notna(inbound_date):

                    inbound_date = pd.to_datetime(
                        inbound_date
                    ).date()

                    est_finish_date = (
                        pd.to_datetime(
                            inbound_date
                        )
                        + timedelta(days=8)
                    ).date()

                if key in existing_keys:

                    row_index = (
                        existing_keys[key]
                    )

                    existing_inbound = (
                        tracker_df.at[
                            row_index,
                            "Inbound Date"
                        ]
                    )

                    existing_finish = (
                        tracker_df.at[
                            row_index,
                            "Est. Finish Date"
                        ]
                    )

                    already_complete = (
                        pd.notna(existing_inbound)
                        and pd.notna(existing_finish)
                        and str(existing_inbound).strip() != ""
                        and str(existing_finish).strip() != ""
                    )

                    if already_complete:

                        rows_skipped += 1
                        continue

                    tracker_df.at[
                        row_index,
                        "QTY"
                    ] = qty

                    if pd.notna(inbound_date):

                        tracker_df.at[
                            row_index,
                            "Inbound Date"
                        ] = str(inbound_date)

                        tracker_df.at[
                            row_index,
                            "Est. Finish Date"
                        ] = str(est_finish_date)

                        rows_updated += 1

                else:

                    tracker_df.loc[
                        len(tracker_df)
                    ] = [
                        invoice_no,
                        item_no,
                        qty,
                        str(inbound_date)
                        if pd.notna(inbound_date)
                        else "",
                        str(est_finish_date)
                        if est_finish_date is not None
                        else ""
                    ]

                    rows_added += 1

            tracker_df.to_excel(
                label_status_file,
                index=False
            )

            print(
                f"Added   : {rows_added}"
            )

            print(
                f"Updated : {rows_updated}"
            )

            print(
                f"Skipped : {rows_skipped}"
            )

            print(
                f"Saved   : {label_status_file.name}"
            )

        except Exception as e:

            print(
                f"ERROR : {invoice_no}"
            )

            print(str(e))