# HMTOOL: Hydro-Meteorological Tool

This web application demonstrates the power of Javascript and Python as client-side and server-side programming languages, respectively.

This "Demo Prototype" aims to support a framework for managing an environmental observatory information system [1]. The ideas behind this prototype are as follows:

- Data Collection: Data input from several data sources like data from on-field stations, web services, APIs, files, etc. Thus, nature of the input data is very varied.
- Data Processing: Some cleaning and standardization analysis, ...
- Data Presentation: The final user can perform several operations, such as reading plots from real time data, etc.  

Users can access the application using their Google account. Data are stored in Google Datastore (NoSQL).

## Motivation
- Real time data processing
- Open standardization such as [OGC][8] 
- Visualization intensive
- Variety of analisys that can be applied
- IoT trend 
- Popular field for applying Machine Learning techniques

## Cloud Environment
- [App Engine][2]
- [Google Datastore][3]

## Language
- [Javascript][4]
- [Python][5]

## Dependencies
- [webapp2][6]
- [jinja2][7]

[1]: http://www.sciencedirect.com/science/article/pii/S009830041000275X
[2]: https://developers.google.com/appengine
[3]: https://cloud.google.com/datastore/docs/concepts/overview
[4]: https://www.javascript.com/
[5]: https://python.org
[6]: http://webapp-improved.appspot.com/
[7]: http://jinja.pocoo.org/docs/
[8]: http://www.opengeospatial.org/

## Locally run

To locally run the project for development purposes
    ```dev_appserver.py .```


To locally run the project and clean the datastore
    ```dev_appserver.py . dev_appserver.py . --clear_datastore```

