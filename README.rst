Lambda Scrapers
=========

Commands to create package:

```
cd in virtualenv site-packages, like cd ~/Envs/lambda-scrapers/lib/python3.6/site-packages/
zip -r9 ~/python/lambda-scrapers.zip .
cd in lambda-scrapers project
zip -g ~/python/lambda-scrapers.zip *.py

```

Upload your package to AWS lambda service.

Fill event like TO_SCRAPE_EXAMPLE.
Make sure that your URLs don't contain products that aren't in scraping scope.

If you are using sandbox version of Amazon SES, make sure that you have
verified sender and receiver emails in AWS console.