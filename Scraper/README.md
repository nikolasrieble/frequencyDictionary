Local test 

`docker build -t scraper .`

`docker run -p 5000:5000 scraper`

Deployment 

`heroku container:push web -a scraping-backend`

`heroku container:release web -a scraping-backend`
