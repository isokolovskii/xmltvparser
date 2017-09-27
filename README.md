# Xml TV Parser #

This application is a part of TV project group aimed to deliver great experience in browsing TV schedule. 

This is xml parser which parses xmltv file format with TV schedule and puts it into MySQL database.

## Contents: ##
#### logger.py ####
Logger class based on logging module. Creates project-level directory log for logging. Support both release and debug
logging. Uses rotating file handler for logs rotation.

#### database.py ####
Database class based on mysql connector. Creates initial tables if they don't exists. Can execute queries or prepare
a query and then run it on given parameters. Handles errors and returns Error object for class user error handling.

#### xmltvparser.py ####
Xml parsing class based on Xml ElementTree parser. Loads xmltv file and then parses it into MySQL database.

#### tvparser.py ####
Application entry point. Creates Xml parser and runs it. 