# Data2Excel

Excel Report Generator for Oracle Hyperion FDMEE


## Simple workflow for this programm

In Jython script you will connect to database and execute needed queries. Format result of query as json_like string and write it to some temp file on disk.
Next pass file path to this json file to Rust executable and wait untill it create a report in Excel format.


