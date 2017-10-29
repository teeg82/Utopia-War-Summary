import mechanize
from bs4 import BeautifulSoup
import urllib2
import cookielib
import re
import logging
import sys

cook = cookielib.CookieJar()
req = mechanize.Browser()
req.set_cookiejar(cook)

UTOPIA_HOME = "http://utopia-game.com/shared/"
KINGDOM_NEWS = "http://utopia-game.com/wol/game/kingdom_news"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] is not None:
        logging.basicConfig(level=logging.DEBUG)

    logging.debug("Opening credentials file")
    file = open('credentials.txt', 'r')
    credentials = file.readlines()
    username = credentials[0].strip()
    password = credentials[1].strip()
    import pdb; pdb.set_trace()

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
            text = ' '.join(row.text.strip().split())
            monthly_summary.append(text)
            row = row.find_next('tr')
            if row is None:
                break

        if incomplete_summary:
            previous = req.find_link(predicate=lambda link: (dict(link.attrs).get('class') or 'nope') == 'previous')
            if previous is not None:
                logging.debug("Loading previous kingdom news at url %s" % previous.absolute_url)
                req.follow_link(link=previous)
        war_summary += reversed(monthly_summary)

    war_summary = reversed(war_summary)
    print "\n".join(war_summary)
