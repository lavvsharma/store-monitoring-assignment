"""
Author: Lav Sharma
Created on: 1st Nov 2023
"""

from datetime import datetime
from typing import Union

from retrying import retry
from sqlalchemy import exists
from sqlalchemy.exc import ProgrammingError, DatabaseError, OperationalError

import store_monitoring_das.configuration as config
from store_monitoring_das.CommonEnums import RequestLifeCycle
from store_monitoring_das.CommonEnums import ResponseCode, HttpResponseCode
from store_monitoring_das.database.Session import get_db
from store_monitoring_das.entity.DatabaseModels import Request
from store_monitoring_das.exception import SQLException
from store_monitoring_das.ModuleLogger import setup_logger

logger = setup_logger()


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def create_entry_in_request() -> dict:
    """
        Description: This function is used to create an entry in the Request table.
    """
    try:
        current_utc_time = datetime.utcnow()
        create_response = dict()

        request_entry = Request(R_RequestReceivedTimestamp=current_utc_time,
                                RS_Id=RequestLifeCycle.Request_Received.value)

        with get_db() as session_object:
            try:
                # ========================================================================
                # Create entry in the Request table
                # ========================================================================
                session_object.add(request_entry)
                session_object.commit()

            except OperationalError as operational_error:
                logger.error('Error connecting to the MYSQL Server.Invalid database IP or Port provided' +
                             f'\nError-{str(operational_error)}', exc_info=True)
                raise operational_error

            except ProgrammingError as programming_error:
                logger.error('Wrong/Invalid/Unknown database name provided' +
                             f'\nError-{str(programming_error)}', exc_info=True)
                raise programming_error

            except Exception as error:
                # ========================================================================
                # Handle the exception and rollback the session_object
                # ========================================================================
                session_object.rollback()
                logger.error('Error in creating entry in Request' +
                             f'\nError - {str(error)}', exc_info=True)

                create_response['Entry_Created'] = False
                create_response['ResponseCode'] = ResponseCode.Record_Create_Fail.value

            # ========================================================================
            # Retrieve the added row
            # ========================================================================
            added_row = session_object.query(request_entry.__class__).get(
                request_entry.R_Id)

        if added_row:
            # ========================================================================
            # Entry successfully created in the db
            # ========================================================================
            logger.info('Entry created in Request')

            create_response['Entry_Created'] = True
            create_response['R_Id'] = vars(added_row)['R_Id']
            create_response['ResponseCode'] = ResponseCode.Record_Create_Success.value

        else:
            logger.error('Error in creating entry in Request', exc_info=True)

            create_response['Entry_Created'] = False
            create_response['ResponseCode'] = ResponseCode.Record_Create_Fail.value

        create_response['HttpResponseCode'] = HttpResponseCode.Success.value
        return create_response

    except Exception as error:
        logger.error(f'Error in creating entry in Request, Exception - {str(error)}', exc_info=True)


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def check_if_row_exists_in_request(request_id: int) -> dict:
    """
        Description: This function is used to check that given a request_id whether
        a record exists in the Request table or not.
        If Yes --> Returns True
        Else --> Returns False
    """
    try:
        row_exists = dict()

        with get_db() as session_object:
            if session_object.query(exists().where(
                    Request.R_Id == request_id)).scalar():
                row_exists['RecordExists'] = True
                row_exists['Input'] = dict()
                row_exists['Input']['Request_Id'] = request_id
                row_exists['ResponseCode'] = ResponseCode.Record_Found.value

            else:
                row_exists['RecordExists'] = False
                row_exists['Input'] = dict()
                row_exists['Input']['Request_Id'] = request_id
                row_exists['ResponseCode'] = ResponseCode.Record_Not_Found.value

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
        logger.error(f'Error in exists query of the database, Request_Id - {str(request_id)}' +
                     f'\nException - {str(error)}', exc_info=True)


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def read_row_from_the_request(request_id: int) -> dict:
    """
        Description: This function is used to read a row from the Request table,
        given a request_id. It will first check whether a row for the given request_id
        exists or not in the database.
        If Yes --> it will retrieve the row from the database
        If no --> it will return a ResponseCode of Record_Not_Found
    """
    try:
        read_row_output = dict()

        # ========================================================================
        # Check if the row exists in the Request table or not
        # ========================================================================
        record = check_if_row_exists_in_request(request_id)

        if 'RecordExists' in record:
            if record['RecordExists']:
                # ========================================================================
                # If the entry exists in the database, then retrieve the row
                # ========================================================================
                with get_db() as session_object:
                    row_entry = session_object.query(Request).filter(
                        Request.R_Id == request_id).first()

                read_row_output['Row'] = vars(row_entry)
                read_row_output['RecordExists'] = record['RecordExists']
                read_row_output['Input'] = dict()
                read_row_output['Input']['Request_Id'] = request_id
                read_row_output['ResponseCode'] = ResponseCode.Record_Read_Success.value

            else:
                # ========================================================================
                # Row does not exist in the database
                # ========================================================================
                read_row_output['RecordExists'] = record['RecordExists']
                read_row_output['Input'] = dict()
                read_row_output['Input']['Request_Id'] = request_id
                read_row_output['ResponseCode'] = ResponseCode.Record_Not_Found.value

        else:
            # ========================================================================
            # Internal DB Error
            # ========================================================================
            logger.error(f'Error in check_if_row_exists_in_request, Request_Id - {str(request_id)}', exc_info=True)

            read_row_output['Input'] = dict()
            read_row_output['Input']['Request_Id'] = request_id
            read_row_output['ResponseCode'] = ResponseCode.Database_Error.value

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
        logger.error('Error in retrieving row for value Request_Id -' + str(request_id)
                     + f'\nException - {str(error)}', exc_info=True)


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DATABASE_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_IN_MILLISECONDS,
       retry_on_exception=SQLException.retry_if_mysql_error)
def update_row_in_adapter_request(request_id: int,
                                  update_row_column_name: str,
                                  update_row_column_value: Union[int, str, datetime]) -> dict:
    """
        Description: This function is used to update a row in Request table.
        It will check whether for the given request_id a record is present or not.
            If Yes --> update the row.
            If No --> return Record_Not_Found ResponseCode
        If No --> Returns Column_Does_Not_Exists ResponseCode
    """
    try:
        update_row_response = dict()

        # ========================================================================
        # Check if the row exists for the given request_id
        # ========================================================================
        read_row = check_if_row_exists_in_request(request_id)

        if 'RecordExists' in read_row:
            if read_row['RecordExists']:
                with get_db() as session_object:
                    # ========================================================================
                    # Record found, update the row
                    # ========================================================================
                    no_of_rows_updated = session_object.query(Request).filter(
                        Request.R_Id == request_id).update(
                        {getattr(Request, update_row_column_name): update_row_column_value},
                        synchronize_session=False)
                    session_object.commit()

                if no_of_rows_updated == 1:
                    update_row_response['Successful_Update'] = True
                    update_row_response['Input'] = dict()
                    update_row_response['Input']['Request_Id'] = request_id
                    update_row_response['Input']['ColumnName'] = update_row_column_name
                    update_row_response['Input']['ColumnValue'] = update_row_column_value
                    update_row_response['ResponseCode'] = ResponseCode.Record_Update_Success.value

                else:
                    # ========================================================================
                    # Record not updated
                    # ========================================================================
                    logger.error('Record not updated' +
                                 f'\nRequest_Id-{str(request_id)}' +
                                 f'\nColumnName-{str(update_row_column_name)}' +
                                 f'\nColumnValue-{str(update_row_column_value)}', exc_info=True)

                    update_row_response['Successful_Update'] = False
                    update_row_response['Input'] = dict()
                    update_row_response['Input']['Request_Id'] = request_id
                    update_row_response['Input']['ColumnName'] = update_row_column_name
                    update_row_response['Input']['ColumnValue'] = update_row_column_value
                    update_row_response['ResponseCode'] = ResponseCode.Record_Not_Found.value

            else:
                # ========================================================================
                # Record not updated
                # ========================================================================
                logger.error('Record not updated' +
                             f'\nRequest_Id-{str(request_id)}' +
                             f'\nColumnName-{str(update_row_column_name)}' +
                             f'\nColumnValue-{str(update_row_column_value)}', exc_info=True)

                # ========================================================================
                # Send response as Record_Not_Found
                # ========================================================================
                update_row_response['Successful_Update'] = False
                update_row_response['Input'] = dict()
                update_row_response['Input']['Request_Id'] = request_id
                update_row_response['Input']['ColumnName'] = update_row_column_name
                update_row_response['Input']['ColumnValue'] = update_row_column_value
                update_row_response['ResponseCode'] = ResponseCode.Record_Not_Found.value

        else:
            # ========================================================================
            # Internal DB Error
            # ========================================================================
            logger.error('Error in check_if_row_exists_in_adapter_request',
                         f'\nRequest_Id - {str(request_id)}', exc_info=True)

            update_row_response['Successful_Update'] = False
            update_row_response['Input'] = dict()
            update_row_response['Input']['Request_Id'] = request_id
            update_row_response['Input']['ColumnName'] = update_row_column_name
            update_row_response['Input']['ColumnValue'] = update_row_column_value
            update_row_response['ResponseCode'] = ResponseCode.Database_Error.value

        update_row_response['HttpResponseCode'] = HttpResponseCode.Success.value
        return update_row_response

    except ProgrammingError as mysql_programming_error:
        logger.error('Wrong/Invalid/Unknown database name provided' +
                     f'\nError-{str(mysql_programming_error)}', exc_info=True)
        raise mysql_programming_error

    except DatabaseError as mysql_database_error:
        logger.error('Error connecting to the MYSQL Server.Invalid database IP or Port provided' +
                     f'\nError-{str(mysql_database_error)}', exc_info=True)
        raise mysql_database_error

    except Exception as error:
        logger.error(f'Error in Updating value for Request_Id - {str(request_id)}'
                     f'\n{str(update_row_column_name)}-{str(update_row_column_value)}' +
                     f'\nException - {str(error)}', exc_info=True)
