"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

import os
from datetime import datetime

import pandas

import store_monitoring.configuration as config
from store_monitoring.CommonEnums import RequestLifeCycle
from store_monitoring.DASHelper import update_request
from store_monitoring.Helper import convert_timestamp_utc_to_local_timezone, \
    identify_day_for_timezone, read_unique_stores_wrapper, read_store_timezone_wrapper, read_store_status_wrapper, \
    read_store_details_wrapper, time_it
from store_monitoring.ModuleLogger import setup_logger
from store_monitoring.processing.TimeNotSpecified import process_store_for_24_7
from store_monitoring.processing.TimeSpecified import process_store_with_specified_time

logger = setup_logger()


@time_it
def generate_report(request_id: int):
    try:
        store_uptime_and_downtime = []

        # ====================================================================
        # Read all the unique StoreId's from the database
        # ====================================================================
        store_ids = read_unique_stores_wrapper()
        logger.info(f'Total StoreIds - {str(len(store_ids))}')

        # ====================================================================
        # Update RequestStatus in the DB
        # ====================================================================
        update_request(request_id=request_id,
                       update_row_column_name='RS_Id',
                       update_row_column_value=RequestLifeCycle.Processing_Request.value)
        logger.info(f'Updated RequestStatus as {str(RequestLifeCycle.Processing_Request.value)} '
                    f'for request_id - {str(request_id)}')

        for counter, store_id in enumerate(store_ids, start=1):
            store_output = process_store(counter, store_id)
            store_uptime_and_downtime.append(store_output)

        # ====================================================================
        # Filter out None values from store_uptime_and_downtime
        # ====================================================================
        filtered_store_uptime_and_downtime = [output for output in store_uptime_and_downtime if output is not None]
        store_uptime_and_downtime_df = pandas.DataFrame(filtered_store_uptime_and_downtime)

        # ====================================================================
        # Store the output in the OUTPUT_CSV_PATH
        # ====================================================================
        output_path = os.path.join(config.OUTPUT_CSV_PATH, f'{str(request_id)}.csv')
        store_uptime_and_downtime_df.to_csv(output_path, index=False)

        request_completed_timestamp = datetime.utcnow()
        # ====================================================================
        # Update RequestCompletedTimestamp in the DB
        # ====================================================================
        update_request(request_id=request_id,
                       update_row_column_name='R_RequestCompletedTimestamp',
                       update_row_column_value=request_completed_timestamp)
        logger.info(f'Updated R_RequestCompletedTimestamp as {str(request_completed_timestamp)} '
                    f'for request_id - {str(request_id)}')

        # ====================================================================
        # Update RequestStatus in the DB
        # ====================================================================
        update_request(request_id=request_id,
                       update_row_column_name='RS_Id',
                       update_row_column_value=RequestLifeCycle.Processing_Completed.value)
        logger.info(f'Updated RequestStatus as {str(RequestLifeCycle.Processing_Completed.value)} '
                    f'for request_id - {str(request_id)}')

        # ====================================================================
        # Update OutputPath in the DB
        # ====================================================================
        update_request(request_id=request_id,
                       update_row_column_name='R_OutputFilePath',
                       update_row_column_value=output_path)
        logger.info(f'Updated R_OutputFilePath as {str(output_path)} for request_id - {str(request_id)}')

    except Exception:
        # ====================================================================
        # Update RequestStatus in the DB
        # ====================================================================
        update_request(request_id=request_id,
                       update_row_column_name='RS_Id',
                       update_row_column_value=RequestLifeCycle.Error_In_Processing_Request.value)
        logger.error(f'Updated RequestStatus as {str(RequestLifeCycle.Error_In_Processing_Request.value)} '
                     f'for request_id - {str(request_id)}')
        raise


@time_it
def process_store(counter: int,
                  store_id: str) -> dict:
    try:
        logger.info(f'Processing store_id - {str(store_id)}')
        # ====================================================================
        # Get the Timezone for the StoreId from StoreTimezone table
        # ====================================================================
        store_timezone = read_store_timezone_wrapper(store_id)

        # ====================================================================
        # Read all the records for StoreId from the StoreStatus table
        # ====================================================================
        store_status = read_store_status_wrapper(store_id)
        if len(store_status) > 0:
            store_status_df = pandas.DataFrame(store_status)

            # ====================================================================
            # Convert timestamps to the local timezone
            # ====================================================================
            store_status_df = convert_timestamp_utc_to_local_timezone(store_status_df, store_timezone)
            store_status_df = identify_day_for_timezone(store_status_df)

            # ====================================================================
            # Read the StoreDetails using StoreId, which will give us the StartTime and EndTime of the store
            # If no rows found consider that the store was open 24*7
            # ====================================================================
            store_details = read_store_details_wrapper(store_id)
            if len(store_details) > 0:
                return process_store_with_specified_time(store_details, store_status_df, store_id)

            else:
                # ====================================================================
                # print(f'Store is open 24*7, StoreId - {str(store_id)}')
                # ====================================================================
                return process_store_for_24_7(store_status_df, store_id)

    except Exception:
        raise


if __name__ == '__main__':
    generate_report()
