# ArcGIS Layer Updating

Python script to sync layers in ArcGIS pertaining to ESC monitoring and repairs.

## Notes

ArcGIS Cloud login credentials are stored in local environment variables for security.

Code is hosted on a Ubuntu Linux server provided by [Linode](https://www.linode.com) and run every 5 minuites using a CronJob. This repo is kept in-sync with the server through another CronJob. 