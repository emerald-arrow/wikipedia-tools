# Generating tables with sessions results

## Description
The **results_table.py** script generates tables with results of test/free practice/qualifying sessions and races. The table is generated based on provided *Classification.CSV* file downloaded from one of Alkamelsystems websites.

Supported Alkamelsystems websites:
- [FIA WEC](fiawec.alkamelsystems.com)
- [IMSA](results.imsa.com)
- [ELMS](elms.alkamelsystems.com)

The **db.py** file contains dictionaries which allow to reduce amount of work on results tables by inserting right values like flags, article links etc.
- *drivers_ACO* dictionary contains codes of countries that ACO/FIA uses in their results files
- *drivers* dictionary contains drivers data: flags and text that should appear next to their flags (either article link or plain text)
- *teams* dictionary contains teams data: flags and text that should appear next to their flags (either article link or plain text)
- *cars* dictionary contains links to Wikipedia articles about cars

The **db_cars.py** script generates data for *cars* dictionary in **db.py**. The script works with .CSV results of test/free practice/qualifying practice sessions and races.

The **db_drivers.py** script generates data for *drivers* dictionary in **db.py**. The script doesn not work with .CSV results of ACO/FIA races.

The **db_teams.py** script generates data for *teams* dictionary in **db.py**. The script cannot obtain flags from .CSV results of ACO/FIA races. In case of IMSA .CSV results, the script cannot obtain flags as IMSA does not include them in any results files.