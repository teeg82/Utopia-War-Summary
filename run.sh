#! /bin/sh

source slack.sh

docker-compose -p war_summary $@
# docker run --rm -it --name utopia_war_summary -e SLACK_TOKEN=$SLACK_TOKEN paulrichter/utopia_war_summary:2.0 uws
