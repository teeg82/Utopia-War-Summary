#! /bin/sh

cd ./app
docker build -t paulrichter/utopia_war_summary:2.0 .

cd ../db
docker build -t paulrichter/camelot_db:1.0 .

cd ..
