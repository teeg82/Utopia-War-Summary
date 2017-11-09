import html2text
import mechanize
from mechanize import LinkNotFoundError
from bs4 import BeautifulSoup
import urllib2
import cookielib
import re
import logging
import sys
from slacker import Slacker
import os

reload(sys)
sys.setdefaultencoding('utf8')

cook = cookielib.CookieJar()
req = mechanize.Browser()
req.set_cookiejar(cook)

UTOPIA_HOME = "http://utopia-game.com/shared/"
KINGDOM_NEWS = "http://utopia-game.com/wol/game/kingdom_news"
FORMATTER_HOME = "http://home-world.org/utopia/formatter/"

SLACK_TOKEN = os.getenv('SLACK_TOKEN', '')

if len(sys.argv) > 1 and sys.argv[1] is not None:
    logging.basicConfig(level=logging.DEBUG)

def fetch():
    logging.debug("Opening credentials file")
    file = open('credentials.txt', 'r')
    credentials = file.readlines()
    username = credentials[0].strip()
    password = credentials[1].strip()

    logging.debug("Connecting to %s" % UTOPIA_HOME)
    req.open(UTOPIA_HOME)

    signin_form_index = None
    for index, form in enumerate(req.forms()):
        if form.attrs['id'] == 'signInForm':
            signin_form_index = index
            break;

    # If this was none, we might already be logged in (for some reason)
    # Otherwise, log in
    if signin_form_index is not None:
        logging.debug("Logging in...")
        req.select_form(nr=signin_form_index)
        req.form['username'] = username
        req.form['password'] = password
        req.submit()
        logging.debug("Login appears to be successful")

    logging.debug("Opening kingdom news")
    req.open(KINGDOM_NEWS)

    war_summary = []

    incomplete_summary = True
    # Work backwards from the most recent, until the beginning of the war is found
    while incomplete_summary:
        soup = BeautifulSoup(req.response().read(), "html5lib")

        monthly_summary = []
        # If the war declaration line is on this page, it means this is the point that the war began.
        # In that case, this will be the last iteration because we now have the entire war history.
        war_declaration = soup(text=re.compile(r"has declared WAR with our kingdom!"))
        if war_declaration is not None and len(war_declaration) > 0:
            logging.debug("War declaration line found.")
            # Start at the war declaration line
            row = war_declaration[0].findPrevious('tr')
            incomplete_summary = False
        else:
            logging.debug("No war declaration line found. Scraping page from the top.")
            table = soup.find('table', {'id': 'news'})
            # Start at the top
            row = table.find_all('tbody')[0].find_all('tr')[0]

        # Work your way down to the bottom of the news table
        while True:
            text = row.text.strip()
            # Don't add empty rows (this usually occurs at the very beginning of the age)
            if len(text) > 0:
                text = ' '.join(row.text.strip().split())
                monthly_summary.append(text)
            row = row.find_next('tr')
            if row is None:
                break

        if incomplete_summary:
            try:
                previous = req.find_link(predicate=lambda link: (dict(link.attrs).get('class') or 'nope') == 'previous')
                if previous is not None:
                    logging.debug("Loading previous kingdom news at url %s" % previous.absolute_url)
                    req.follow_link(link=previous)
            except LinkNotFoundError as e:
                logging.info("Link to 'Previous' not found. Start of age reached.")
                incomplete_summary = False
        war_summary += reversed(monthly_summary)

    if len(war_summary) == 0:
        logging.debug("War summary size was zero. No kingdom news was found. Is this the beginning of the age?")
        print "Could not find any kingdom news. Either this is the beginning of the age, or something horrible has happened."
    else:
        logging.debug("Compiling war summary.")
        war_summary = reversed(war_summary)
        war_summary_text = "\n".join(war_summary)
        # print war_summary_text

        formatted_summary = fetch_summary(war_summary_text)
        post_summary(formatted_summary)


def fetch_summary(war_summary_text):
    req.open(FORMATTER_HOME)
    logging.debug("Submitting war summary to formatter")
    req.select_form(name="post")
    req.form['data'] = war_summary_text
    req.submit()
    logging.debug("War summary submission appears to be successful.")

    # results
    soup = BeautifulSoup(req.response().read().encode('utf-8'), "html5lib")
    results = soup.find('div', {'class': 'heading'})
    # chart_land

    summary_html = []
    summary_html.append(str(results))
    while True:
        results = results.nextSibling
        summary_html.append(str(results))
        if hasattr(results, 'has_attr') and results.has_attr('class'):
            # We've reached the end
            if 'highlights' in results.attrs['class']:
                summary_html.append(str(results.nextSibling))
                break;

    formatted_summary = html2text.html2text("".join(summary_html))
    formatted_summary = formatted_summary.replace("\n\n", "\n")
    print formatted_summary
    return formatted_summary


def post_summary(war_summary_text):
    logging.debug("Posting message to slack")
    slack = Slacker(SLACK_TOKEN)
    slack.files.upload(channels='#war-summary', content=war_summary_text, filename="war_summary", title="War Summary")
    logging.debug("Slack should have received the message.")


if __name__ == "__main__":
    fetch()
