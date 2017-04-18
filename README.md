# science-cruise-data-management
Django application to track data from events in the ACE cruise

All this code was used during the Antarctic Circumpolar Expedition (ACE) 2017. About 30.000 samples, 4000 events, 3 months of GPSs data, 3 months of weather information were registered in this system. Used by more than 150 scientists.

The problem is that we knew 0, zero Django until 2 weeks before starting the expedition. We developed the system during the 10 days before going to the Antarctic and a big part of the system was developed while sailing on the Akademik Tryoshnikov, supporting scientists with their works, without good Internet connection and in a hurry.

We tried to keep the code expedition independent so it could be used for other expeditions later on. But in some places a pragmatic decision had to be taken due to our time and resources constraints and expedition specific code has been introduced in the system. For example specific ways to read spreadsheets that should be configurable.

The code has been done without best practises: due to the lack of time there were no time for refactoring, unit tests (!!! I seriously apologise) or even code reviews. Or to keep code more indepdendent.

I wouldn't use this code as it comes but would need some changes: the events and sample importers, add unit tests, etc.

Some parts like the gps importer could be improved but it uses interesting techniques to import GPS files in real time into the database.
