#Author: R. Gayathri 
#Month Created: July 2026

import pandas as pd
from pathlib import Path

from modules.edc.file_finder import get_item_list_file
from modules.edc.expiry_extractor import extract_expiry_map
from modules.rfid.rfid_checker import add_rfid_remark


def generate_edc_file(run_folder):

    # ------------------------------------
    # Find Item List
    # ------------------------------------

    item_list_file = get_item_list_file(
        run_folder
    )

    print(
        f"Item List Found : {item_list_file}"
    )

    # ------------------------------------
    # Read Excel
    # ------------------------------------

    df = pd.read_excel(
        item_list_file,
        engine="openpyxl"
    )

    # ------------------------------------
    # Build Expiry Map
    # ------------------------------------

    expiry_map = extract_expiry_map(
        run_folder
    )

    # ------------------------------------
    # Required Columns
    # ------------------------------------

    edc_df = df[
        [
            "Delivery",
            "Material",
            "Item Description",
            "Batch",
            "Actual delivery qty"
        ]
    ].copy()

    edc_df.columns = [
        "Delivery",
        "Item Number",
        "Description",
        "Lot Number",
        "Qty"
    ]

    # ------------------------------------
    # Remove Empty Qty Rows
    # ------------------------------------

    edc_df = edc_df[
        edc_df["Qty"] > 0
    ]

    # ------------------------------------
    # Expiry Date Mapping
    # ------------------------------------

    edc_df["Expiry Date"] = edc_df.apply(
        lambda row: expiry_map.get(
            (
                str(row["Item Number"]).strip(),
                str(row["Lot Number"]).strip()
            ),
            ""
        ),
        axis=1
    )

    matched_expiry = (
        edc_df["Expiry Date"]
        .astype(str)
        .str.strip()
        .ne("")
        .sum()
    )

    print(
        f"Expiry Matches : {matched_expiry}"
    )

    # ------------------------------------
    # RFID Validation
    # ------------------------------------

    edc_df = add_rfid_remark(
        edc_df,
        r"C:\Users\11070043\OneDrive - BD\Shipment Automation Tool\config\RFID items.xlsx"  #Path to be changed in client laptop
    )

    rfid_matches = (
        edc_df["Remarks"]
        .eq("RFID needed")
        .sum()
    )

    print(
        f"RFID Matches : {rfid_matches}"
    )

    # ------------------------------------
    # Output Folder
    # ------------------------------------

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

    shipment_no = run_folder.name

    output_file = (
        output_folder /
        f"{shipment_no}.xlsx"
    )

    # ------------------------------------
    # Save Output
    # ------------------------------------

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

        edc_df.to_excel(
            writer,
            sheet_name="Sheet1",
            index=False,
            startrow=3
        )

    print(
        f"\nRows Processed : {len(edc_df)}"
    )

    print(
        f"Output Created : {output_file}"
    )

    return edc_df