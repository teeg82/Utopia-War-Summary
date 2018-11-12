# Installation

[Install Docker](https://docs.docker.com/engine/installation/#supported-platforms)

Build the docker image from the project root using `./build.sh`.

## But I don't want to install docker!

- Install Python 2.7 (https://www.python.org/download/releases/2.7/)
- (Optional) install Virtualenv (https://virtualenv.pypa.io/en/stable/installation/)
- (Optional) Create a virtualenv environment for the summary and activate it
- Run `RUN pip install beautifulsoup4 requests mechanize`

# Usage

### Utopia Credentials
Add your username and password to the `credentials.txt` file on seperate lines. DO NOT COMMIT THIS FILE (unless you want me hacking your account). Example:

```
theRoundTable
myPasssword123
```

### Slack token
Add the slack token to the `slack.sh` file. Contact the_round_table for the token. DO NOT COMMIT THIS FILE EVER! (Slack monitors github, they will automatically disable the code if it gets committed, which means the bot won’t work until I regenerate a new one). Example:

```
export SLACK_TOKEN=token123
```

### Setting up the database
Currently the summary bot shares the same database as the glory wall. It is therefore necessary to clone the glorywall repo as well.

```
git clone https://github.com/teeg82/Camelot_Glory_Wall2.git

cd Camelot_Glory_Wall2

./build.sh && run.sh up -d db

cd ../Utopia-War-Summary
```

### Setting up the table(s)
```
docker cp ./db/summary.sql camelot_db_1:/tmp/summary.sql

docker exec -it camelot_db_1 su-exec postgres psql camelot -f /tmp/summary.sql
```
You should see a line that says "CREATE TABLE", if successful. Report any errors.

### Running the bot
When you want to run the bot and generate a summary, this is what I typically do

```./build.sh && ./run.sh up -d bot && docker attach war_summary_bot_1```

That command will rebuild the docker container, run it, and attach the console to the running container (up until it dies). This process allows you to set breakpoints in the code (using `import; pdb.set_trace()`); the console will break at that line, allowing you to debug and interact.
