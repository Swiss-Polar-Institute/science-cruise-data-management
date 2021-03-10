# science-cruise-data-management
Django application to enter events, samples, metadata records during a science cruise. Additionally creates an intranet: documents, small utilities like changing coordinate systems, where the ship was at a given time, announcements, ferrybox visualization, etc.

This code was used during the Antarctic Circumpolar Expedition (ACE) 2017. Around 30,000 samples, 4,000 events, 3 months of GPS data and weather information were recorded in this system.

At the time of buildling this system, we knew no Django at all. It was developed during the two weeks before going to the Antarctic and a large part of it was developed while sailing on the Akademik Tryoshnikov during ACE whilst supporting scientists with their work, without a good Internet connection and in a hurry. Having said that, we learnt a lot and added features during the expedition to meet the needs of those on board, providing visualisation of data, summary reports and small utilities. 

Our intention was to keep the code "expedition-independent" so it could be used by other expeditions later on. But in many places and for practicality, code specific to our expedition is in the repository instead of being part of the settings or data driven. For example specific ways to read spreadsheets that should be configurable, are hard coded in the code.

The code was written without best practises: due to the lack of time there was no time for refactoring, unit tests (!!! I seriously apologise), documentation or even code reviews.

I wouldn't use this code as it comes but rather as a prototype or starting point for refactoring: It all worked but could be done in a much better way.

Some parts like the GPS importer could be improved but it this particular part does use interesting techniques to import GPS files in real-time into the database.

For more information see the [documentation](https://github.com/Swiss-Polar-Institute/science-cruise-data-management/tree/master/documentation) which has a list of features and screenshots.

Please get in touch: Carles Pina (carles@pina.cat or carles.pinaestany@swisspolar.ch) and Jen Thomas (jen@falciot.net or jen.thomas@swisspolar.ch), ACE 2016-2017.

## Commands

### geteventdatetimes.py
From a csv file containing the event numbers, output another csv file containing the event numbers and datetimes associated with these. An event can have an instantaneous time, or a start and end time, so it accounts for this possibility.
