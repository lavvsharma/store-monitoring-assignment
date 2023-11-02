# store_monitoring

### Installation

To run this it can be directly installed by using python pip / pip3

```sh
$ pip3 install store_monitoring==1.0.0
```

### File Structure

```
├── store_monitoring
|   └── data
|       └── config.ini
|   └── entity
|       └── __init__.py
|       └── Models.py
|   └── exception
|       └── __init__.py
|       └── ConnectionError.py
|   └── processing
|       └── __init__.py
|       └── GenerateReport.py
|       └── TimeNotSpecified.py
|       └── TimeSpecified.py
|   ├── __init__.py
|   ├── CommonEnums.py
|   ├── configuration.py
|   ├── DASHelper.py
|   ├── Helper.py
|   ├── ModuleLogger.py
|   ├── StoreMonitoring.py
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
        i. This API endpoint is a health check for the Store Monitoring to check the status of the service, whether the service is up and running or not.
2. /trigger_report
    a. Method - POST
    b. Input - NA
    c. Description
        i. This API endpoint is used to trigger the generation of the report.
        ii. It will create an entry in the Request table and return a report_id for the user to track the report.
c. /get_report/{report_id}
    a. Method - GET
    b. Input 
        i. report_id
    c. Description
        i. This API endpoint is used to get the status given a report_id.
```

