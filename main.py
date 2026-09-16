#Author: R.Gayathri
#Date Created: July 2026


from pathlib import Path
import traceback

from modules.utils.config_loader import (
    load_config
)

from modules.logging.logger import (
    get_logger
)

from modules.status.status_manager import (
    update_status
)

# from modules.sync.master_data_sync import (
#     sync_master_files
# )

#from modules.sync.input_sync import (
    #sync_input_files
#)

from modules.queue.input.input_scanner import (
    get_pending_shipments
)

from modules.queue.processing_log import (
    log_success,
    log_failed
)

from modules.edc.edc_generator import (
    generate_edc_file
)

from modules.notify_dk.notify_dk_generator import (
    generate_notify_dk
)

logger = get_logger()


def main():

    logger.info(
        "Shipment Automation Started"
    )

    update_status(
        "Generate Files",
        "RUNNING"
    )

    # sync_master_files()

    #sync_input_files()

    pending_shipments = (
        get_pending_shipments()
    )

    print(
        "\nPending Shipments"
    )

    print(
        "--------------------"
    )

    for shipment in pending_shipments:

        print(
            shipment
        )

    if not pending_shipments:

        print(
            "\nNo shipments found."
        )

        update_status(
            "Generate Files",
            "NOT RUN"
        )

        return

    success_count = 0

    for shipment in pending_shipments:

        shipment_no = (
            shipment[
                "ShipmentNo"
            ]
        )

        shipment_type = (
            shipment[
                "Type"
            ]
        )

        run_folder = (
            Path(
                shipment[
                    "FolderPath"
                ]
            )
        )

        print(
            "\n----------------------"
        )

        print(
            f"Type : {shipment_type}"
        )

        print(
            f"Shipment No : {shipment_no}"
        )

        print(
            f"Run Folder : {run_folder}"
        )

        try:

            if shipment_type == "EDC":

                print(
                    "ENTERED EDC BLOCK"
                )

                generate_edc_file(
                    run_folder
                )

            elif shipment_type == "GDC":

                print(
                    "ENTERED GDC BLOCK"
                )

                generate_notify_dk(
                    run_folder,
                    r"C:\Users\11070043\OneDrive - BD\Shipment Automation Tool\config\RFID items.xlsx"   #Path to be changed in client laptops 
                )

            log_success(
                shipment_no
            )

            success_count += 1

            logger.info(
                f"{shipment_no} Completed"
            )

        except FileNotFoundError as e:

            print(
                f"\nWARNING : {shipment_no}"
            )

            print(
                f"Reason : {e}"
            )

            logger.warning(
                f"{shipment_no} skipped - {e}"
            )

            continue

        except Exception as e:

            print(
                "\nERROR OCCURRED"
            )

            traceback.print_exc()

            logger.exception(e)

            log_failed(
                shipment_no,
                str(e)
            )

            update_status(
                "Generate Files",
                "FAILED"
            )

            return

    if success_count > 0:

        update_status(
            "Generate Files",
            "SUCCESS"
        )

        print(
            "\nPROCESS COMPLETED SUCCESSFULLY"
        )

    else:

        update_status(
            "Generate Files",
            "NOT RUN"
        )

        print(
            "\nNO OUTPUT FILES GENERATED"
        )


if __name__ == "__main__":

    main()