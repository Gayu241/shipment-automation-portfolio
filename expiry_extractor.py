#Author: R.Gayathri
#Date Created: July 2026


import fitz
import re
from pathlib import Path


def extract_expiry_map(run_folder):

    expiry_map = {}

    pdf_files = list(
        Path(run_folder).glob("*.pdf")
    )

    print(f"\nPDF Files Found : {len(pdf_files)}")

    for pdf in pdf_files:

        pdf_name = pdf.name.upper()

        print(f"\nProcessing : {pdf.name}")

        try:

            doc = fitz.open(str(pdf))

            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            # ==========================================
            # STER PDF
            # ==========================================

            if "STER" in pdf_name:

                pattern = re.compile(
                    r'([A-Z0-9\-]+)\s+'
                    r'\d+\s+'
                    r'([A-Z0-9]+)\s+'
                    r'\d{2}/\d{2}/\d{4}\s+'
                    r'(\d{2}/\d{2}/\d{4})'
                )

                matches = pattern.findall(text)

                print(
                    f"STER Records Found : {len(matches)}"
                )

                for item_no, lot_no, expiry in matches:

                    expiry_map[
                        (
                            item_no.strip(),
                            lot_no.strip()
                        )
                    ] = expiry

            # ==========================================
            # INVOICE PDF
            # ==========================================

            elif "INV" in pdf_name:

                invoice_pattern = re.compile(

                    r'(\d+)\s+'
                    r'([A-Z0-9\-]+).*?'
                    r'Batch:\s*([A-Z0-9]+).*?'
                    r'Expiry date:\s*(\d{2}/\d{2}/\d{4})',

                    re.DOTALL
                )

                matches = invoice_pattern.findall(text)

                print(
                    f"INV Records Found : {len(matches)}"
                )

                for _, item_no, lot_no, expiry in matches:

                    key = (
                        item_no.strip(),
                        lot_no.strip()
                    )

                    if key not in expiry_map:

                        expiry_map[key] = expiry

            # ==========================================
            # DELIVERY NOTE PDF
            # ==========================================

            elif "DN" in pdf_name:

                dn_pattern = re.compile(
                    r'([A-Z0-9]+)\s+(\d{2}/\d{2}/\d{4})'
                )

                matches = dn_pattern.findall(text)

                print(
                    f"DN Records Found : {len(matches)}"
                )

                # Keeping DN processing for future
                # Currently not merging because
                # DN does not reliably provide
                # Item Number + Batch mapping

        except Exception as e:

            print(
                f"Failed Processing : {pdf.name}"
            )

            print(e)

    # ==========================================
    # CLEANUP
    # ==========================================

    clean_expiry_map = {}

    for (item_no, lot_no), expiry in expiry_map.items():

        if item_no in [
            "UNKNOWN",
            "O",
            "I",
            ""
        ]:
            continue

        clean_expiry_map[
            (
                item_no.strip(),
                lot_no.strip()
            )
        ] = expiry

    print(
        f"\nClean Records Found : {len(clean_expiry_map)}"
    )

    return clean_expiry_map