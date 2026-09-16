import pandas as pd
import zipfile


def add_rfid_remark(df, rfid_file):

    if zipfile.is_zipfile(rfid_file):

        rfid_df = pd.read_excel(
            rfid_file,
            engine="openpyxl"
        )

    else:

        rfid_df = pd.read_excel(
            rfid_file,
            engine="xlrd"
        )

    rfid_df.columns = rfid_df.columns.str.strip()

    rfid_items = set(
        rfid_df["ITEM"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    df["Remarks"] = (
        df["Item Number"]
        .astype(str)
        .str.strip()
        .str.upper()
        .apply(
            lambda x:
            "RFID needed"
            if x in rfid_items
            else ""
        )
    )

    return df