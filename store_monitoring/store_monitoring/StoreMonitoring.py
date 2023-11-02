"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

import logging
import threading

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import store_monitoring.configuration as config
from store_monitoring import __appname__, __version__, __description__
from store_monitoring.CommonEnums import RequestLifeCycle
from store_monitoring.DASHelper import create_request, read_request, update_request
from store_monitoring.Helper import read_csv_file
from store_monitoring.entity.Models import HeartbeatResult
from store_monitoring.ModuleLogger import setup_logger
from store_monitoring.processing.GenerateReport import generate_report

logger = setup_logger()


class StoreMonitoring:
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
            logging.error(f'Exception - {str(error)}', exc_info=True)

    def add_routes(self):
        @self.app.get('/healthcheck', tags=["Heartbeat"])
        async def get_heartbeat():
            """
            This API call is used to check Healthcheck of StoreMonitoring.
            """
            try:
                logging.info('/healthcheck accessed')
                heartbeat = HeartbeatResult(is_alive=True)

                return {
                    'IsAlive': heartbeat.is_alive,
                    'AppName': __appname__,
                    'Version': __version__,
                    'Description': __description__
                }

            except Exception as error:
                logging.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.get('/trigger_report', tags=['Store Monitoring'])
        async def trigger_report() -> dict:
            """
            This API is used to trigger the report generation.
            It is used to generate the report for the restaurants up-time and down-time.
            """
            try:
                # ===================================================================
                # Create entry in the Request table
                # ===================================================================
                create_request_response = create_request()
                if 'ResponseCode' in create_request_response and create_request_response['HttpResponseCode'] == 200:
                    if 'HttpResponseCode' in create_request_response and create_request_response[
                        'ResponseCode'] == 2000:

                        # ===================================================================
                        # Process the request on a different thread
                        # ===================================================================
                        generate_report_obj = threading.Thread(
                            target=generate_report, args=(create_request_response['R_Id'],))
                        generate_report_obj.start()

                        # ===================================================================
                        # Update RequestStatus in the DB
                        # ===================================================================
                        update_request(request_id=create_request_response['R_Id'],
                                       update_row_column_name='RS_Id',
                                       update_row_column_value=RequestLifeCycle.Processing_Request.value)
                        logger.info(f'Updated RS_Id as {str(RequestLifeCycle.Processing_Request.value)} '
                                    f'for request_id - {str(create_request_response["R_Id"])}')
                        return {'report_id': create_request_response['R_Id']}

                    else:
                        return {'Message': 'Error in processing report'}

                else:
                    return {'Message': 'Error in processing report'}

            except Exception as error:
                logging.error(f'Exception - {str(error)}', exc_info=True)

        @self.app.post('/get_report/{report_id}', tags=['Store Monitoring'])
        async def get_report(report_id: int):
            """
            This API is used to check the status of the report given a report id.
            """
            try:
                # ===================================================================
                # Read the status of the report from the Request table
                # ===================================================================
                read_request_response = read_request(report_id)

                # ===================================================================
                # Check the status
                # ===================================================================
                if 'Row' in read_request_response:

                    if 'RS_Id' in read_request_response['Row'] and read_request_response['Row'][
                        'RS_Id'] == RequestLifeCycle.Request_Received.value:
                        return {'Message': 'Request received'}

                    elif 'RS_Id' in read_request_response['Row'] and read_request_response['Row'][
                        'RS_Id'] == RequestLifeCycle.Request_Sent_For_Processing.value:
                        return {'Message': 'Request sent for processing'}

                    elif 'RS_Id' in read_request_response['Row'] and read_request_response['Row'][
                        'RS_Id'] == RequestLifeCycle.Processing_Request.value:
                        return {'Message': 'Processing'}

                    elif 'RS_Id' in read_request_response['Row'] and read_request_response['Row'][
                        'RS_Id'] == RequestLifeCycle.Error_In_Processing_Request.value:
                        return {'Message': 'Error in processing request'}

                    elif 'RS_Id' in read_request_response['Row'] and read_request_response['Row'][
                        'RS_Id'] == RequestLifeCycle.Processing_Completed.value:
                        if 'R_OutputFilePath' in read_request_response['Row']:
                            output_file_path = read_request_response['Row']['R_OutputFilePath']
                            csv_data = read_csv_file(output_file_path)
                            return {'Message': 'Completed',
                                    'CSV_Output': csv_data}

            except Exception as error:
                logging.error(f'Exception - {str(error)}', exc_info=True)

    def run(self, host, port):
        try:
            logger.info(f'Started StoreMonitoring on {str(host)}:{str(port)}')
            uvicorn.run(self.app, host=host, port=port)

        except Exception as error:
            logging.error(f'Exception - {str(error)}', exc_info=True)


if __name__ == "__main__":
    app = StoreMonitoring(appname=__appname__, version=__version__, description=__description__)
    app.run(host=config.HOST_IP, port=config.HOST_PORT)
