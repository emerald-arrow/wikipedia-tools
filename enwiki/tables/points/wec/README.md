# FIA World Endurance Championship season classification

## Description
It is a script that creates points table of a drivers/teams/manufacturers classification based on HTML table from [FIA WEC official website](https://fiawec.com).

## Details
Using a browser's developer tools it is needed to copy HTML code of a classification table. An example request sent by the browser looks like:

``GET https://www.fiawec.com/en/season/result_search/4153?ranking_id=2440``

Such request is sent after choosing "Season" from navigation bar at the top of the website and clicking "Classification". Any change of classification causes browser to send another request for right classification table in HTML.