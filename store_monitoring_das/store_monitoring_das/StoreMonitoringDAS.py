"""
Author: Lav Sharma
Created on: 28th Oct 2023
"""

from datetime import datetime
from typing import Union

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import store_monitoring_das.configuration as config
from store_monitoring_das import __appname__, __version__, __description__
from store_monitoring_das.entity.Models import HeartbeatResult
from store_monitoring_das.ModuleLogger import setup_logger
from store_monitoring_das.operations.Request import create_entry_in_request, read_row_from_the_request, \
    update_row_in_adapter_request
from store_monitoring_das.operations.StoreDetails import read_all_rows_from_store_details
from store_monitoring_das.operations.StoreStatus import read_unique_rows_from_store_status, \
    read_all_rows_from_store_status
from store_monitoring_das.operations.StoreTimezone import read_row_from_store_timezone

logger = setup_logger()


class StoreMonitoringDAS:
    def __init__(self, appname, version, description):
        try:
            self.app = FastAPI(title=appname, version=version, description=description)
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config.ORIGINS,
                allow_credentials=config.ALLOW_CREDENTIALS,
                allow_methods=config.ALLOWED_METHODS,
                allow_headers=config.ALLOW_HEADERS,
            )
            self.add_routes()

        except Exception as error:
            logger.error(f'Exception - {str(error)}', exc_info=True)

    def add_routes(self):
        @self.app.get('/healthcheck', tags=["Heartbeat"])
        async def get_heartbeat():
            """
            This API call is used to check Healthcheck of StoreMonitoringDAS.
            """
            try:
                heartbeat = HeartbeatResult(is_alive=True)

                return {
                    'IsAlive': heartbeat.is_alive,
                    'AppName': __appname__,
                    'Version': __version__,
                    'Description': __description__
                }

            except Exception as error:
                logger.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.post('/store/{store_id}', tags=['StoreDetails'])
        async def read_store_details(store_id: str,
                                     order_by: str = None):
            """
            This API call is used to fetch all the rows from StoreDetails given a store_id, order_by is optional.
            Accepted values of order_by are given below. The rows are order by on SD_Day column.
            1. If you want the rows in ascending specify 'asc'.
            2. If you want the rows in descending specify 'desc'.
            """
            try:
                logger.info(f'Reading all rows for store_id - {str(store_id)}, order_by - {str(order_by)}')
                return read_all_rows_from_store_details(store_id, order_by)

            except Exception as error:
                logger.error(f'Exception - {str(error)}' +
                             f'Inputs - store_id - {str(store_id)}, order_by - {str(order_by)}', exc_info=True)

        @self.app.get('/unique/stores', tags=['StoreStatus'])
        async def read_rows_from_store_status():
            """
            This API call is used to read all the unique StoreId's from the StoreStatus table.
            """
            try:
                logger.info('Reading unique stores from StoreStatus')
                return read_unique_rows_from_store_status()

            except Exception as error:
                logger.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.post('/store_status/{store_id}', tags=['StoreStatus'])
        async def read_store_status(store_id: str,
                                    order_by: str = None):
            """
            This API call is used read all the rows from the StoreStatus table given a store_id.
            order_by is optional. Accepted values are given below. The rows are order by on SS_TimestampUtc column.
            1. If you want the rows in ascending specify 'asc'.
            2. If you want the rows in descending specify 'desc'.
            """
            try:
                logger.info(f'Reading rows from StoreStatus for store_id - {str(store_id)}, order_by - {str(order_by)}')
                return read_all_rows_from_store_status(store_id, order_by)

            except Exception as error:
                logger.error(f'Exception - {str(error)}' +
                             f'Inputs - store_id - {str(store_id)}', exc_info=True)

        @self.app.get('/store/{store_id}/timezone', tags=['StoreTimezone'])
        async def read_store_timezone(store_id: str):
            """
            This API call is used to read a row from the StoreTimezone table.
            """
            try:
                logger.info(f'Reading store timezone store_id - {str(store_id)}')
                return read_row_from_store_timezone(store_id)

            except Exception as error:
                logger.error(f'Exception - {str(error)}' +
                             f'Inputs - store_id - {str(store_id)}', exc_info=True)

        @self.app.post('/request/create', tags=['Request'])
        async def create_request():
            """
            This API is used to create an entry in the Request table for every user request.
            """
            try:
                logger.info('Create entry in request')
                return create_entry_in_request()

            except Exception as error:
                logger.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.get('/request/read/{request_id}', tags=['Request'])
        async def read_request(request_id: int):
            """
            This API is used to read an entry from the Request table given a request_id.
            """
            try:
                logger.info(f'Reading row from Request, request_id - {str(request_id)}')
                return read_row_from_the_request(request_id)

            except Exception as error:
                logger.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.post('/request/update/{request_id}', tags=['Request'])
        async def update_request(request_id: int,
                                 update_row_column_name: str,
                                 update_row_column_value: Union[int, str, datetime]):
            """
            This API is used to update entry in the Request table given a request_id.
            """
            try:
                logger.info(f'Updating row in Request, request_id - {str(request_id)},'
                            f', update_row_column_name - {str(update_row_column_name)}'
                            f', update_row_column_value - {str(update_row_column_value)}')
                return update_row_in_adapter_request(request_id,
                                                     update_row_column_name,
                                                     update_row_column_value)

            except Exception as error:
                logger.error(f'Exception - {str(error)}', exc_info=True)

    def run(self, host, port):
        try:
            logger.info(f'Started StoreMonitoring DAS on {str(host)}:{str(port)}')
            uvicorn.run(self.app, host=host, port=port)

        except Exception as error:
            logger.error(f'Exception - {str(error)}', exc_info=True)


if __name__ == "__main__":
    app = StoreMonitoringDAS(appname=__appname__, version=__version__, description=__description__)
    app.run(host=config.HOST_IP, port=config.HOST_PORT)
