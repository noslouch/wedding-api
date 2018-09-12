## tests

`$ docker-compose -f docker-compose-test.yml run web python manage.py test`

## dev

### rebuild dev image
`$ docker build -f Dockerfile-dev -t wedding-api .`

### connect to database
`$ docker run --rm -it --env-file .env wedding-api python manage.py shell_plus`
