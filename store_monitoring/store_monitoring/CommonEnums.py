"""
Author: Lav Sharma
Created on: 29th Oct 2023
"""

from enum import Enum


class StoreMonitoringDASUrl(Enum):
    Read_Store_Details = '/store/{store_id}'
    Read_Unique_Stores = '/unique/stores'
    Read_Store_Status = '/store_status/{store_id}'
    Read_Store_Timezone = '/store/{store_id}/timezone'
    Create_Request = '/request/create'
    Read_Request = '/request/read/{request_id}'
    Update_Request = '/request/update/{request_id}'


class RequestLifeCycle(Enum):
    Request_Received = 1
    Request_Sent_For_Processing = 2
    Processing_Request = 3
    Processing_Completed = 4
    Error_In_Processing_Request = 5
