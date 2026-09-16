from pathlib import Path

import pandas as pd
import pyodbc


def generate_t8_po():

    print("\n==============================")
    print("T8 PO FILE REFRESH STARTED")
    print("==============================\n")

    conn_str = (
        "DRIVER={SQL Server};"
        "SERVER=pwsgp339terp08;"
        "DATABASE=T8ERP;"
        "Trusted_Connection=yes;"
    )

    query = """
    SELECT TOP 1000
       m.BillDate      AS [PO# Date],
       m.BillNo        AS [PO#],
       c.X_UPC         AS [Item #],        
       d.UnTransSQty   AS [Open QTY],
       d.SQuantity     AS [Order QTY],
       d.DeliveryDate  AS [Delivery Date]
    FROM purBillOrderMaster m
    INNER JOIN purBillOrderDetail d
       ON m.BillNo = d.BillNo
    LEFT JOIN comMaterial c
       ON d.MaterialId = c.MaterialId
    ORDER BY m.BillDate DESC
    """

    print("Connecting to T8...")

    conn = pyodbc.connect(
        conn_str,
        timeout=30
    )

    print("Connected Successfully")

    print("\nExecuting Query...")

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    print(
        f"Rows Retrieved : {len(df)}"
    )

    print("\nCreating Output Folder...")

    output_folder = (
        Path("Output")
        / "T8 PO"
    )

    output_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_folder
        / "T8_PO.xlsx"
    )

    print("\nWriting Excel File...")

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name="Open PO"
        )

        worksheet = writer.sheets[
            "Open PO"
        ]

        for column in worksheet.columns:

            max_length = 0

            column_letter = (
                column[0]
                .column_letter
            )

            for cell in column:

                try:

                    cell_length = len(
                        str(cell.value)
                    )

                    if cell_length > max_length:

                        max_length = (
                            cell_length
                        )

                except Exception:

                    pass

            worksheet.column_dimensions[
                column_letter
            ].width = max_length + 2

    print(
        f"\nT8 PO Updated : {output_file}"
    )

    print("\n==============================")
    print("T8 PO REFRESH COMPLETED")
    print("==============================\n")

    return output_file


if __name__ == "__main__":

    generate_t8_po()