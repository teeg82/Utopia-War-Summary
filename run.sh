#! /bin/sh

source slack.sh

docker run --rm --name utopia_war_summary -e SLACK_TOKEN=$SLACK_TOKEN paulrichter/utopia_war_summary:1.0 uws
#| pbcopy
