# quiz_bot

Simple telegram quiz bot 

### How to use:

#### Add .env file:
    cp docker/.env.example docker/.env

#### Add your bot token in new .env file:

    BOT_TOKEN=

#### Run the local server:

    docker compose up -d --build
    docker compose logs -f worker
