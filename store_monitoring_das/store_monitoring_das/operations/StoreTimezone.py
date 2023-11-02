"""
Author: Lav Sharma
Created on: 28th Oct 2023
"""

from retrying import retry
from sqlalchemy import exists
from sqlalchemy.exc import ProgrammingError, DatabaseError

import store_monitoring_das.configuration as config
from store_monitoring_das.CommonEnums import ResponseCode, HttpResponseCode
from store_monitoring_das.database.Session import get_db
from store_monitoring_das.entity.DatabaseModels import StoreTimezone
from store_monitoring_das.exception import SQLException
from store_monitoring_das.ModuleLogger import setup_logger

logger = setup_logger()


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def read_row_from_store_timezone(store_id: str):
    """
        Description: This function is used to read a row from the StoreTimezone table,
        given a store_id. It will first check whether a row for the given store_id
        exists or not in the database.
        If Yes --> it will retrieve the row from the database
        If no --> it will return a ResponseCode of Record_Not_Found
    """
    try:
        read_row_output = dict()

        # ========================================================================
        # Check if the row exists in the StoreTimezone table or not
        # ========================================================================
        record = check_if_row_exists_in_store_timezone(store_id)

        if 'RecordExists' in record:
            if record['RecordExists']:
                # ========================================================================
                # If the entry exists in the database, then retrieve the row
                # ========================================================================
                with get_db() as session_object:
                    row_entry = session_object.query(StoreTimezone).filter(StoreTimezone.SD_StoreId == store_id).first()

                read_row_output['Row'] = vars(row_entry)
                read_row_output['ResponseCode'] = ResponseCode.Record_Read_Success.value

            else:
                # ========================================================================
                # Row does not exist in the database
                # ========================================================================
                read_row_output['ResponseCode'] = ResponseCode.Record_Not_Found.value

            read_row_output['RecordExists'] = record['RecordExists']

        else:
            # ========================================================================
            # Internal DB Error
            # ========================================================================
            logger.error('Error in check_if_row_exists_in_adapter_request',
                         f'\nInput - {str(store_id)}', exc_info=True)
            read_row_output['ResponseCode'] = ResponseCode.Database_Error.value

        read_row_output['Input'] = dict()
        read_row_output['Input']['StoreId'] = store_id
        read_row_output['HttpResponseCode'] = HttpResponseCode.Success.value
        return read_row_output

    except ProgrammingError as mysql_programming_error:
        logger.error('Wrong/Invalid/Unknown database name provided' +
                     f'\nError-{str(mysql_programming_error)}', exc_info=True)
        raise mysql_programming_error

    except DatabaseError as mysql_database_error:
        logger.error('Error connecting to the MYSQL Server.Invalid database IP or Port provided' +
                     f'\nError-{str(mysql_database_error)}', exc_info=True)
        raise mysql_database_error

    except Exception as error:
        logger.error(f'Error in retrieving row from StoreTimezone, for StoreId - {str(store_id)}'
                     + f'\nException - {str(error)}', exc_info=True)


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def check_if_row_exists_in_store_timezone(store_id: str) -> dict:
    """
        Description: This function is used to check that given a store_id whether
        a record exists in the StoreTimezone table or not.
        If Yes --> Returns True
        Else --> Returns False
    """
    try:
        row_exists = dict()

        with get_db() as session_object:
            if session_object.query(exists().where(StoreTimezone.SD_StoreId == store_id)).scalar():
                row_exists['RecordExists'] = True
                row_exists['ResponseCode'] = ResponseCode.Record_Found.value

            else:
                row_exists['RecordExists'] = False
                row_exists['ResponseCode'] = ResponseCode.Record_Not_Found.value

            row_exists['Input'] = dict()
            row_exists['Input']['StoreId'] = store_id
            row_exists['HttpResponseCode'] = HttpResponseCode.Success.value
            return row_exists

    except ProgrammingError as mysql_programming_error:
        logger.error('Wrong/Invalid/Unknown database name provided' +
                     f'\nError-{str(mysql_programming_error)}', exc_info=True)
        raise mysql_programming_error

    except DatabaseError as mysql_database_error:
        logger.error('Error connecting to the MYSQL Server.Invalid database IP or Port provided' +
                     f'\nError-{str(mysql_database_error)}', exc_info=True)
        raise mysql_database_error

    except Exception as error:
        logger.error('Error in exists query of the StoreTimezone table' +
                     f'\n Input - {str(store_id)}' +
                     f'\nException - {str(error)}', exc_info=True)
