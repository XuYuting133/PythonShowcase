# README


## About The Project
This set of scripts were developed for GE5219 Group Project: **Supporting Real-Time Traffic Information Dashboard With Python Scripting.**

## About The Authors
NUS Master of Applied GIS Programme, Class of 2021

*GE5219 Spatial Programming, Group 10*

* Luo Laiwen 
* Qi Ruiyuan 
* Xu Yuting 


## Dashboard Design
The dashboard is built on ArcGIS Dashboards on ArcGIS Online. It is available to the public for viewing at: https://bit.ly/32deMtC. For more information on ArcGIS Dashboards, please visit the page [here](https://www.esri.com/en-us/arcgis/products/arcgis-dashboards/overview#:~:text=ArcGIS%20Dashboards%20enables%20users%20to,visualizations%20on%20a%20single%20screen.&text=Dashboards%20are%20essential%20information%20products,component%20to%20your%20geospatial%20infrastructure.).


## Runtime
Average runtime from 3 readings is taken. 
Before testing the scripts, kindly take note that due to data size and the need to avoid exceeding LTA Data Mall API rate limit, **some scripts will take more than an hour to complete.**
- GetPassengerVolume.py: 1875.31s
- GetBusStops.py: 375.96s
- GetTrafficSpeedBand.py: 3880.81s
- GetTaxiDensity.py: 169.36s
- GetEstimatedTravelTime.py: 98.24s
- GetTrafficCameraImages.py: 242.31s
- GetTrafficIncidents.py: 52.58s
- GetTaxiAvailability.py: 196.93s

## Using the scripts
The scripts were written for full automation. Hence, you can execute the scripts directly without providing any additional inputs.
The necessary libraries/packages required, other than the standard Python libraries, are:
- ArcGIS API for Python (the API comes with any ArcGIS Pro installation. Alternatively, you may do a standalone installation following the guide [here](https://support.esri.com/en/technical-article/000022005))


## Code Workspace Organisation
Three classes of scripts can be found in this repository.

**1. Utilities scripts**

These scripts contain variables/constants and customized funtions that are repeatedly used by the core tasks. These variables/constants/functions are saved in standalone modules to facilitate ease of maintenance in the future, should there be a need to amend these variables/functions. 

These scripts include:
- constants.py
- CommonModules.py

Before using the utility scripts, first import them into the code.

```python
import constants
import CommonModules
```

**2. Core task scripts**

These scripts perform the core task of querying data from LTA Data Mall and updating them on ArcGIS Online feature services. Depending on how frequently the data is updated at LTA, these scripts are further classified into:


*2a. Regular Tasks*

These scripts handle datasets that are updated frequently (e.g. less than 10 min), including:
- GetEstimatedTravelTime.py
- GetTaxiAvailability.py
- GetTrafficCameraImages.py
- GetTrafficIncidents.py

*2b. Hourly Tasks*

These scripts are executed every hour to get a snapshot of the data, including:
- GetTaxiDensity.py

*2c. Daily Tasks*

These scripts handle datasets that are updated at a frequency of longer than a day, including:
- GetBusStop.py
- GetTrafficSpeedBand.py

*2d. One-Off Tasks*

These scripts handle datasets that only need to be updated once for the dashboard, and will only be run on demand in ad-hoc frequency. 
- GetPassengerVolume.py



**3. Key References**

- ESRI (n.d.) API Reference for the ArcGIS API for Python (v1.8.5). https://developers.arcgis.com/python/api-reference/
- Land Transport Authority (19 Jan 2021). LTA Data Mall API User Guide & Documentation. https://datamall.lta.gov.sg/content/dam/datamall/datasets/LTA_DataMall_API_User_Guide.pdf
- OneMap (n.d.). OneMap API Documentation. https://www.onemap.gov.sg/docs/#introduction
- Google (n.d.). Places API. https://developers.google.com/maps/documentation/places/web-service/overview 
