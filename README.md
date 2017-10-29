# Purpose

This script will 

# Installation

[Install Docker](https://docs.docker.com/engine/installation/#supported-platforms)

Build the docker image from the project root using `./build.sh`.

## But I don't want to install docker!

- Install Python 2.7 (https://www.python.org/download/releases/2.7/)
- (Optional) install Virtualenv (https://virtualenv.pypa.io/en/stable/installation/)
- (Optional) Create a virtualenv environment for the summary and activate it
- Run `RUN pip install beautifulsoup4 requests mechanize`

# Usage

Add your username and password to the `credentials.txt` file on seperate lines. Example:

```
theRoundTable
myPasssword123
```

From the project root, run `./run.sh`, or 

```
docker run --rm paulrichter/utopia_war_summary:1.0 uws`
```

You may also output the results to a file:

```
docker run --rm paulrichter/utopia_war_summary:1.0 uws > summary.txt
```

To view verbose output:

```
docker run --rm -e VERBOSE=VERBOSE paulrichter/utopia_war_summary:1.0 uws
```
