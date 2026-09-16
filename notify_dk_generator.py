#Author: R.Gayathri
#Date Created: July 2026
import pandas as pd
from pathlib import Path

from modules.rfid.rfid_checker import add_rfid_remark
from modules.utils.file_finder import get_shipment_excel


def generate_notify_dk(run_folder, rfid_file):

    # --------------------------------------------------
    # Locate Shipment Excel File
    # --------------------------------------------------

    shipment_file = get_shipment_excel(
        run_folder
    )

    print(
        f"Shipment File Found : {shipment_file}"
    )

    # --------------------------------------------------
    # Read Shipment Excel
    # --------------------------------------------------

    df = pd.read_excel(
        shipment_file,
        engine="openpyxl"
    )

    # --------------------------------------------------
    # Build Notify Data
    # --------------------------------------------------

    notify_df = df[
        [
            "Item Number",
            "Cust Po Number",
            "Total Qty Eaches",
            "Lot Number",
            "Expiration Date"
        ]
    ].copy()

    notify_df.columns = [
        "Item Number",
        "Cust Po Number",
        "Qty",
        "Lot Number",
        "Expiration Date"
    ]

    # --------------------------------------------------
    # RFID Validation
    # --------------------------------------------------

    notify_df = add_rfid_remark(
        notify_df,
        rfid_file
    )

    # --------------------------------------------------
    # Run Statistics
    # --------------------------------------------------

    shipment_rows = len(notify_df)

    rfid_matches = (
        notify_df["Remarks"]
        .eq("RFID needed")
        .sum()
    )

    print(
        f"Shipment Rows : {shipment_rows}"
    )

    print(
        f"RFID Matches : {rfid_matches}"
    )

    # --------------------------------------------------
    # Create Output Folder
    # --------------------------------------------------

    run_folder_name = Path(
        run_folder
    ).name

    output_folder = Path(
        f"output/{run_folder_name}"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------
    # Save Notify File
    # --------------------------------------------------

    shipment_no = run_folder.name

    output_file = (
        output_folder /
        f"{run_folder_name}.xlsx"
    )

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        pd.DataFrame(
            [[shipment_no]]
        ).to_excel(
            writer,
            sheet_name="Sheet1",
            index=False,
            header=False,
            startrow=0
        )

        notify_df.to_excel(
            writer,
            sheet_name="Sheet1",
            index=False,
            startrow=3
        )

    print(
        f"\nNotify DK created : {output_file}"
    )

    return notify_df