# store_monitoring_das

### Installation

To run this it can be directly installed by using python pip / pip3

```sh
$ pip3 install store_monitoring_das==1.0.0
```

### File Structure

```
├── store_monitoring_das
|   └── data
|       └── config.ini
|   └── database
|       └── __init__.py
|       └── Connection.py
|       └── Session.py
|   └── entity
|       └── __init__.py
|       └── DatabaseModels.py
|       └── Models.py
|   └── exception
|       └── __init__.py
|       └── SQLException.py
|   └── operations
|       └── __init__.py
|       └── Request.py
|       └── StoreDetails.py
|       └── StoreStatus.py
|       └── StoreTimezone.py
|   ├── __init__.py
|   ├── CommonEnums.py
|   ├── configuration.py
|   ├── ModuleLogger.py
|   ├── StoreMonitoringDAS.py
├── MANIFEST.in                  
├── README.md
└── setup.py
```

### 1.0.0

```text
1. /healthcheck
    a. Method - GET
    b. Input - NA
    c. Description
        i. This API endpoint is a health check for the Store Monitoring DAS to check the status of the service, whether the service is up and running or not.
2. /store/{store_id}
    a. Method - POST
    b. Input 
        i. store_id - required
        ii. order_by - optional
    c. Description 
        i.This API endpoint is used to fetch all the rows for a given store_id from the StoreDetails table.
        ii. It also accepts order_by, which is used to sort the rows either in ascending order or descending order.
        iii. The rows will be sorted on the basis of SD_Day column which represent the day (0=Monday, 6= Sunday)
3. /unique/stores
    a. Method - GET
    b. Input - NA
    c. Description
        i. This API endpoint is used to fetch all the unique rows from the StoreStatus table.
4. /store_status/{store_id}
    a. Method - POST
    b. Input
        i. store_id - required
        ii. order_by - optional
    c. Description
        i. This API endpoint is used to fetch all the rows from the StoreStatus table given a store_id.
        ii. It also accepts order_by, which is used to sort the rows either in ascending order or descending order.
        ii. The rows will be sorted on the basis of SS_TimestampUtc which represents the timestamp for the store’s.
5. /store/{store_id}/timezone
    a. Method - GET
    b. Input 
        i. store_id
    c. Description
        i. This API endpoint is used to fetch a row from the database for a store_id.
        ii. It represents the timezone for the given store_id.
6. /request/create
    a. Method - POST
    b. Input - NA
    c. Description
        i. This API is used to create an entry in the Request table for every user request that we receive.
7. /request/read/{request_id}
    a. Method - GET
    b. Input
        i. request_id
    c. Description
        i. This API endpoint is used to check the status of the request given a request_id.
8. /request/update/{request_id}
    a. Method - POST
    b. Input
        i. request_id
        ii. update_row_column_name
        ii. update_row_column_value
    c. Description
        i. This API endpoint is used to update a row in the Request table given a request id.
        ii. update_row_column_name - represent which column we need to update.
        ii. update_row_column_value - represent the value of the column.
```

