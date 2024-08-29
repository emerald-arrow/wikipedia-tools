# Points tables

These scripts generate points classifications.

- **points_table.py** — script that prints classification tables based on results saved in database. 
- **elms** — catalog that contains script generating season's classification based on a classification file downloaded from ELMS' official website. README file in this catalog features instructions how to obtain data in .json format used by this script.
- **wec** — catalog that contains script generating season's classification based on classification file downloaded from WEC's official website. README file in this catalog features instructions how to obtain data in .html format used by this script.

Scripts that use downloaded .json/.html files generate less detailed classifications e.g. places below 10th are marked as non-scoring without specifying exact finishing spot. **points.table.py** script generates tables with exact spots/non-finishing statuses, however it lacks support for withdrawals after race weekends start.