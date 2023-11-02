"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

from datetime import datetime
from typing import Union

import requests
from requests.exceptions import ConnectionError as RequestsConnectionError
from retrying import retry

import store_monitoring.configuration as config
from store_monitoring.CommonEnums import StoreMonitoringDASUrl
from store_monitoring.exception import ConnectionError
from store_monitoring.ModuleLogger import setup_logger

logger = setup_logger()


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def read_store_details(store_id: str,
                       order_by: str) -> dict:
    read_store_details_url = ''
    try:
        read_store_details_endpoint = StoreMonitoringDASUrl.Read_Store_Details.value.format(store_id=store_id)
        read_store_details_url = config.STORE_MONITORING_DAS_URL + read_store_details_endpoint
        read_store_details_params = {'order_by': order_by}
        store_details_response = requests.post(url=read_store_details_url, params=read_store_details_params)
        return store_details_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(read_store_details_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(read_store_details_url)}, exc_info=True')
        raise error

    finally:
        del read_store_details_endpoint, read_store_details_url, read_store_details_params


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def read_unique_stores() -> dict:
    read_unique_store_url = ''
    try:
        read_store_details_endpoint = StoreMonitoringDASUrl.Read_Unique_Stores.value
        read_unique_store_url = config.STORE_MONITORING_DAS_URL + read_store_details_endpoint
        unique_store_response = requests.get(url=read_unique_store_url)
        return unique_store_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(read_unique_store_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(read_unique_store_url)}', exc_info=True)
        raise error

    finally:
        del read_store_details_endpoint, read_unique_store_url


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def read_store_status(store_id: str,
                      order_by: str) -> dict:
    read_store_status_url = ''
    try:
        read_store_status_endpoint = StoreMonitoringDASUrl.Read_Store_Status.value.format(store_id=store_id)
        read_store_status_url = config.STORE_MONITORING_DAS_URL + read_store_status_endpoint
        read_store_status_params = {'order_by': order_by}
        store_status_response = requests.post(url=read_store_status_url, params=read_store_status_params)
        return store_status_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(read_store_status_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(read_store_status_url)}', exc_info=True)
        raise error

    finally:
        del read_store_status_endpoint, read_store_status_url, read_store_status_params


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def read_store_timezone(store_id: str) -> dict:
    read_store_timezone_url = ''
    try:
        read_store_timezone_endpoint = StoreMonitoringDASUrl.Read_Store_Timezone.value.format(store_id=store_id)
        read_store_timezone_url = config.STORE_MONITORING_DAS_URL + read_store_timezone_endpoint
        store_timezone_response = requests.get(url=read_store_timezone_url)
        return store_timezone_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(read_store_timezone_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(read_store_timezone_url)}', exc_info=True)
        raise error

    finally:
        del read_store_timezone_endpoint, read_store_timezone_url


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def create_request() -> dict:
    create_request_url = ''
    try:
        create_request_endpoint = StoreMonitoringDASUrl.Create_Request.value
        create_request_url = config.STORE_MONITORING_DAS_URL + create_request_endpoint
        create_request_response = requests.post(url=create_request_url)
        return create_request_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(create_request_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(create_request_url)}', exc_info=True)
        raise error

    finally:
        del create_request_endpoint, create_request_url


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def read_request(request_id: int) -> dict:
    read_request_url = ''
    try:
        read_request_endpoint = StoreMonitoringDASUrl.Read_Request.value.format(request_id=request_id)
        read_request_url = config.STORE_MONITORING_DAS_URL + read_request_endpoint
        read_request_response = requests.get(url=read_request_url)
        return read_request_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(read_request_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(read_request_url)}', exc_info=True)
        raise error

    finally:
        del read_request_endpoint, read_request_url


@retry(stop_max_attempt_number=config.RETRY_ATTEMPT_FOR_DAS_CONNECTION,
       wait_exponential_multiplier=config.WAITING_TIME_BETWEEN_RETRY_FOR_DAS_IN_MILLISECONDS,
       wait_exponential_max=config.MAXIMUM_WAITING_TIME_FOR_RETRY_FOR_DAL_IN_MILLISECONDS,
       retry_on_exception=ConnectionError.retry_if_connection_error)
def update_request(request_id: int,
                   update_row_column_name: str,
                   update_row_column_value: Union[int, str, datetime]) -> dict:
    update_request_url = ''
    try:
        update_request_endpoint = StoreMonitoringDASUrl.Update_Request.value.format(request_id=request_id)
        update_request_url = config.STORE_MONITORING_DAS_URL + update_request_endpoint
        update_request_params = {'update_row_column_name': update_row_column_name,
                                 'update_row_column_value': update_row_column_value}
        update_request_response = requests.post(url=update_request_url, params=update_request_params)
        return update_request_response.json()

    except RequestsConnectionError as request_connection_error:
        logger.error(f'Connection error at - {str(update_request_url)}', exc_info=True)
        raise request_connection_error

    except Exception as error:
        logger.error(f'Exception - {str(error)}' +
                     f'\nURL - {str(update_request_url)}', exc_info=True)
        raise error

    finally:
        del update_request_endpoint, update_request_url
