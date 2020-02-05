# science-cruise-data-management
Django application to enter events, samples, metadata records in a science cruise and also create an intranet: documents, small utilities like changing coordinate systems, where was the ship given a ship time, announcements, ferrybox visualization, etc.

All this code was used during the Antarctic Circumpolar Expedition (ACE) 2017. About 30000 samples, 4000 events, 3 months of GPSs data and weather information were registered in this system. Used by more than 150 scientists.

The problem of the system is that we knew 0, zero Django until 2 weeks before starting the expedition. We developed the system during 2 weeks before going to the Antarctic and a big part of the system was developed while sailing on the Akademik Tryoshnikov during ACE expedition around the Antarctic, supporting scientists with their works, without good Internet connection and in a constant hurry.

We tried to keep the code expedition independent so it could be used by other expeditions later on. But in many places and for practicality code specific to our expedition is in the repository instead of being part of the settings or data driven. For example specific ways to read spreadsheets that should be configurable are hard coded in the code.

The code has been done without best practises: due to the lack of time there were no time for refactoring, unit tests (!!! I seriously apologise), documentation or even code reviews.

I wouldn't use this code as it comes but as a prototype or starting point for a refactoring: it all worked but could be done much better.

Some parts like the GPS importer could be improved but it uses interesting techniques to import GPS files in real time into the database.

[Documentation](https://github.com/cpina/science-cruise-data-management/tree/master/documentation) with a list of features and screenshots.

Carles Pina (carles@pina.cat) and Jen Thomas (jenny_t152@yahoo.co.uk, jenny.thomas@epfl.ch), ACE 2016-2017.

## Commands

### geteventdatetimes.py
From a csv file containing the event numbers, output another csv file containing the event numbers and datetimes associated with these. An event can have an instantaneous time, or a start and end time, so it accounts for this possibility.
