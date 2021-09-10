# Amazon_item_scraper
One of my first Python projects (year 2019). This program used Selenium to log in to Amazon seller central and search trough item listings. The algorithm was trying to convert UPC barcode in to ASIN code with the best sales rank and those ASINs were checked for selling permission. The results were given to another program which was listing the items trough the AWS API. This program was a collaboration with another developer for ComPot ltd – Deyan Rusinov


input file: Input IDs.csv
output file: TOP_ASINs.csv

Info:
	-Get the best ASIN for a list of UPCs passed and check if we are able to sell them.
  
