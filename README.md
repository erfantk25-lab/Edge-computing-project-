# Edge-computing-project-

Copy the example environment file and fill in the values:

```bash
   cp .env.example .env
```

   Required environment variables:

```dotenv
   POSTGRES_DB=sensordb
   POSTGRES_USER=sensordb
   POSTGRES_PASSWORD=<your_password>
```

   > `POSTGRES_DB` and `POSTGRES_USER` should match the values expected by `docker-compose.yml`. Set your own secure value for `POSTGRES_PASSWORD`.