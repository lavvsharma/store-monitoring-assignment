"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

from retrying import retry
from sqlalchemy.exc import ProgrammingError, DatabaseError

import store_monitoring_das.configuration as config
from store_monitoring_das.CommonEnums import OrderBy, ResponseCode, HttpResponseCode
from store_monitoring_das.database.Session import get_db
from store_monitoring_das.entity.DatabaseModels import StoreDetails
from store_monitoring_das.exception import SQLException
from store_monitoring_das.ModuleLogger import setup_logger

logger = setup_logger()


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def read_all_rows_from_store_details(store_id: str,
                                     order_by: str = None):
    try:
        output_response = dict()
        store_details_rows = []
        invalid_order_by_flag = False

        with get_db() as session_object:
            if order_by is None:
                # ========================================================================
                # Fetch all the rows from StoreDetails given a store_id
                # ========================================================================
                row_entry = session_object.query(StoreDetails).filter(
                    StoreDetails.SD_StoreId == store_id).all()

            else:
                if order_by == OrderBy.Ascending.value:
                    # ========================================================================
                    # Fetch all the rows from StoreDetails given a store_id, order by SD_Day asc
                    # ========================================================================
                    row_entry = session_object.query(StoreDetails).filter(
                        StoreDetails.SD_StoreId == store_id).order_by(StoreDetails.SD_Day.asc()).all()

                elif order_by == OrderBy.Descending.value:
                    # ========================================================================
                    # Fetch all the rows from StoreDetails given a store_id, order by SD_Day desc
                    # ========================================================================
                    row_entry = session_object.query(StoreDetails).filter(
                        StoreDetails.SD_StoreId == store_id).order_by(StoreDetails.SD_Day.desc()).all()

                else:
                    # ========================================================================
                    # Invalid order_by specified, throw error
                    # ========================================================================
                    invalid_order_by_flag = True

        output_response['StoreId'] = store_id
        if not invalid_order_by_flag:
            store_details_rows = [vars(row) for row in row_entry]

            if len(store_details_rows) > 0:
                # ========================================================================
                # The list contains more than one rows, hence the read was successful
                # ========================================================================
                output_response['ResponseCode'] = ResponseCode.Record_Read_Success.value

            else:
                # ========================================================================
                # No output in the list, hence no records found
                # ========================================================================
                output_response['ResponseCode'] = ResponseCode.Record_Not_Found.value

        else:
            # ========================================================================
            # Invalid order_by specified
            # ========================================================================
            output_response['ResponseCode'] = ResponseCode.Invalid_Order_By_Choice.value

        output_response['Rows'] = store_details_rows
        output_response['HttpResponseCode'] = HttpResponseCode.Success.value
        return output_response

    except ProgrammingError as mysql_programming_error:
        logger.error('Wrong/Invalid/Unknown database name provided' +
                     f'\nError-{str(mysql_programming_error)}', exc_info=True)
        raise mysql_programming_error

    except DatabaseError as mysql_database_error:
        logger.error('Error connecting to the MYSQL Server.Invalid database IP or Port provided' +
                     f'\nError-{str(mysql_database_error)}', exc_info=True)
        raise mysql_database_error

    except Exception as error:
        logger.error(f'Error in retrieving all rows from StoreDetails, for StoreId - {str(store_id)}'
                     + f'\nException - {str(error)}', exc_info=True)
