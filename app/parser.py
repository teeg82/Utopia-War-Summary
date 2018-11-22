import re
import logging
from datetime import datetime
from db import NewsEntry

UTOPIA_DATE_RE = re.compile(r'^(?P<utopia_date>\w+\s\d{1,2}\sof\sYR\d{1,2})')
DATE_RE = re.compile(r'^(?P<month>\w+)\s(?P<day>\d{1,2})\sof\sYR(?P<year>\d{1,2})')

INBOUND_TRAD_MARCH_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\sinvaded\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)\sand\scaptured\s(?P<acres>\d+)\sacres')
INBOUND_RAZE_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\srazed\s(?P<acres>\d+)\sacres.*\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')
INBOUND_LEARN_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\s.*effectiveness.*scientists\sof\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')
INBOUND_AMBUSH_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\),?\sambushed.*from\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\).*took\s(?P<acres>\d+)\sacres')
# INBOUND_CONQUEST_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\),?\s(?:re)?captured\s(?P<acres>\d+)\sacres.*from\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')

OUTBOUND_TRAD_MARCH_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\scaptured\s(?P<acres>\d+)\sacres.*from\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')
OUTBOUND_RAZE_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\sinvaded\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)\sand\srazed\s(?P<acres>\d+)\sacres')
OUTBOUND_LEARN_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\s.*effectiveness.*scientists\sof\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')
OUTBOUND_AMBUSH_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\)\srecaptured\s(?P<acres>\d+)\sacres\sof\sland\sfrom\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')
OUTBOUND_CONQUEST_RE = re.compile(r'(?P<originator_name>.*\s?)\s\((?P<originator_kingdom>\d{1,2}:\d{1,2})\),\scaptured\s(?P<acres>\d+)\sacres\s\of\sland\sfrom\s(?P<target_name>.*\s?)\s\((?P<target_kingdom>\d{1,2}:\d{1,2})\)')

AID_RE = re.compile(r'(?P<originator>.*\s?)\shas\ssent\san\said\sshipment\sto\s(?P<target>.*\s?)')

WAR_RE = re.compile("declared WAR")

WAR_CATEGORY = "WAR"
INBOUND_TRAD_MARCH_CATAGORY = "INBOUND_TRAD_MARCH"
INBOUND_RAZE_CATEGORY = "INBOUND_RAZE"
INBOUND_LEARN_CATEGORY = "INBOUND_LEARN"
INBOUND_AMBUSH_CATEGORY = "INBOUND_AMBUSH"
INBOUND_CONQUEST_CATEGORY = "INBOUND_CONQUEST"

OUTBOUND_TRAD_MARCH_CATEGORY = "OUTBOUND_TRAD_MARCH"
OUTBOUND_RAZE_CATEGORY = "OUTBOUND_RAZE"
OUTBOUND_LEARN_CATEGORY = "OUTBOUND_LEARN"
OUTBOUND_AMBUSH_CATEGORY = "OUTBOUND_AMBUSH"
OUTBOUND_CONQUEST_CATEGORY = "OUTBOUND_CONQUEST"

AID_CATEGORY = "AID"

processors = {}


def parse_summaries(summaries):
    current_utopia_date = None
    month_order = 1

    logging.info("There are %d news items to parse" % len(summaries))
    for summary in summaries:
        logging.info(summary)

        utopia_date = parse_utopia_date(summary)

        if current_utopia_date != utopia_date or current_utopia_date is None:
            current_utopia_date = utopia_date
            month_order = 1
            # Prune all news entries for this utopia date, as they will be replaced by
            # the new incoming news items
            NewsEntry.delete().where(NewsEntry.utopia_date == utopia_date).execute()

        summary_remainder = summary.replace(utopia_date, "").strip()
        summary_type, results = get_summary_type(summary_remainder)

        processor = processors.get(summary_type, None)
        if processor:
            # logging.info("Parsing a %s news item" % summary_type)
            processor(summary_remainder, results, summary_type, utopia_date, month_order)
            month_order += 1


def parse_utopia_date(summary):
    results = UTOPIA_DATE_RE.search(summary)
    utopia_date = results.group('utopia_date')
    return utopia_date


def get_summary_type(summary):
    results = WAR_RE.search(summary)
    if results:
        return (WAR_CATEGORY, results)
    results = AID_RE.search(summary)
    if results:
        return (AID_CATEGORY, results)
    results = INBOUND_TRAD_MARCH_RE.search(summary)
    if results:
        return (INBOUND_TRAD_MARCH_CATAGORY, results)
    results = INBOUND_RAZE_RE.search(summary)
    if results:
        return (INBOUND_RAZE_CATEGORY, results)
    results = INBOUND_LEARN_RE.search(summary)
    if results:
        return (INBOUND_LEARN_CATEGORY, results)
    results = INBOUND_AMBUSH_RE.search(summary)
    if results:
        return (INBOUND_AMBUSH_CATEGORY, results)
    # results = INBOUND_CONQUEST_RE.search(summary)
    # if results:
    #     return (INBOUND_CONQUEST_CATEGORY, results)
    results = OUTBOUND_TRAD_MARCH_RE.search(summary)
    if results:
        return (OUTBOUND_TRAD_MARCH_CATEGORY, results)
    results = OUTBOUND_RAZE_RE.search(summary)
    if results:
        return (OUTBOUND_RAZE_CATEGORY, results)
    results = OUTBOUND_LEARN_RE.search(summary)
    if results:
        return (OUTBOUND_LEARN_CATEGORY, results)
    results = OUTBOUND_AMBUSH_RE.search(summary)
    if results:
        return (OUTBOUND_AMBUSH_CATEGORY, results)
    results = OUTBOUND_CONQUEST_RE.search(summary)
    if results:
        return (OUTBOUND_CONQUEST_CATEGORY, results)
    return (None, None)


def process_war_declared_summary(summary, results, summary_type, utopia_date, month_order):
    return NewsEntry.create(original_text=summary,
                            news_type=summary_type,
                            utopia_date=utopia_date,
                            month_order=month_order,
                            )


def process_aid_summary(summary, results, summary_type, utopia_date, month_order):
    return NewsEntry.create(original_text=summary,
                            news_type=summary_type,
                            utopia_date=utopia_date,
                            month_order=month_order,
                            )


def calculate_date(utopia_date):
    results = DATE_RE.search(utopia_date)
    month = results.group('month')
    day = results.group('day')
    year = results.group('year')

    # Convert the utopia date to timestamp to make it easier to work with
    date_string = "%(month)s %(day)s %(year)s" % {'month':month, 'day':day.zfill(2), 'year':str(int(year) + 1970)}
    utopia_timestamp = datetime.strptime(date_string, '%B %d %Y')
    return utopia_timestamp


def process_attack_summary(summary, results, summary_type, utopia_date, month_order):
    try:
        originator_name = results.group('originator_name')
        originator_kingdom = results.group('originator_kingdom')
        target_name = results.group('target_name')
        target_kingdom = results.group('target_kingdom')
        acres = results.group('acres')
        calculated_date = calculate_date(utopia_date)

        logging.info("""I found the following data:
            summary: %s
            summary_type: %s
            originator_name: %s
            originator_kingdom: %s
            target_name: %s
            target_kingdom: %s
            acres: %s
            calculated_date: %s
        """ % (summary, summary_type, originator_name, originator_kingdom, target_name, target_kingdom, acres, str(calculated_date)))

        news_entry = NewsEntry.create(original_text=summary,
                                      news_type=summary_type,
                                      utopia_date=utopia_date,
                                      month_order=month_order,
                                      originator=originator_name,
                                      originator_kingdom=originator_kingdom,
                                      target=target_name,
                                      target_kingdom=target_kingdom,
                                      amount=acres,
                                      calculated_date=calculated_date,
                                      )
        return news_entry
    except Exception as ex:
        print(ex)
        logging.error("Something fucked up with this: %s" % summary)


processors[WAR_CATEGORY] = process_war_declared_summary
processors[AID_CATEGORY] = process_aid_summary
processors[INBOUND_TRAD_MARCH_CATAGORY] = process_attack_summary
processors[INBOUND_RAZE_CATEGORY] = process_attack_summary
processors[INBOUND_LEARN_CATEGORY] = process_attack_summary
processors[INBOUND_AMBUSH_CATEGORY] = process_attack_summary
processors[INBOUND_CONQUEST_CATEGORY] = process_attack_summary

processors[OUTBOUND_TRAD_MARCH_CATEGORY] = process_attack_summary
processors[OUTBOUND_RAZE_CATEGORY] = process_attack_summary
processors[OUTBOUND_LEARN_CATEGORY] = process_attack_summary
processors[OUTBOUND_AMBUSH_CATEGORY] = process_attack_summary
processors[OUTBOUND_CONQUEST_CATEGORY] = process_attack_summary
