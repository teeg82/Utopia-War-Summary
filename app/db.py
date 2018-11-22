# NewsEntry
#  - id
#  - original_text
#  - news_type
#  - originator
#  - originator_kingdom
#  - target
#  - target_kingdom
#  - amount
#  - utopia_date
#  - month_order

from peewee import (
    Model,
    PostgresqlDatabase,
    IntegerField,
    AutoField,
    CharField,
    TextField,
    DateTimeField,
)

connection = PostgresqlDatabase('war_summary', user='war_summary', password='war_summary',
                                               host='db', port=5432)

class BaseModel(Model):
    class Meta:
        database = connection

class NewsEntry(BaseModel):
    class Meta:
        db_table = 'camelot_news_entries'

    id = AutoField()
    original_text = TextField()
    news_type = CharField()
    originator = CharField()
    originator_kingdom = CharField()
    target = CharField()
    target_kingdom = CharField()
    amount = IntegerField()
    utopia_date = CharField()
    month_order = CharField()
    calculated_date = DateTimeField()


class ParseLog(BaseModel):
    class Meta:
        db_table = 'camelot_parse_logs'

    id = AutoField()
    original_text = TextField()
    stack_trace = TextField()
    error_type = CharField()


def fetch_own_kingdom_summary():
    query = r"""
    SELECT originator_kingdom, news_type, SUM(amount) as total, count(*) as hits
    FROM camelot_news_entries
    WHERE news_type LIKE %(outbound)s
    group by originator_kingdom, news_type
    """
    results = connection.execute_sql(query, params={'outbound': 'OUTBOUND_%'})
    json_results = {}

def fetch_aggregated_acres():
    query = r"""
        SELECT name, kingdom, sum(acres) as net_acres, sum(hits_against) as hits_against, sum(hits_for) as hits_for
        FROM
        (
            SELECT
                (CASE WHEN news_type LIKE %(inbound)s THEN target ELSE originator END) as name,
                (CASE WHEN news_type LIKE %(inbound)s THEN target_kingdom ELSE originator_kingdom END) as kingdom,
                (
                  CASE
                    WHEN news_type IN ('INBOUND_TRAD_MARCH', 'INBOUND_AMBUSH', 'INBOUND_CONQUEST') THEN -amount
                    WHEN news_type IN ('INBOUND_LEARN', 'INBOUND_RAZE', 'INBOUND_MASSACRE') THEN 0
                    ELSE amount
                  END
                ) as acres,
                (CASE WHEN news_type LIKE %(inbound)s THEN 1 ELSE 0 END) as hits_against,
                (CASE WHEN news_type LIKE %(outbound)s THEN 1 ELSE 0 END) as hits_for
            FROM camelot_news_entries
            WHERE news_type LIKE %(inbound)s OR news_type LIKE %(outbound)s

            UNION ALL

            SELECT
                (CASE WHEN news_type like %(inbound)s THEN originator ELSE target END) as name,
                (CASE WHEN news_type like %(inbound)s THEN originator_kingdom ELSE target_kingdom END) as kingdom,
                (
                  CASE
                    WHEN news_type IN ('INBOUND_TRAD_MARCH', 'INBOUND_AMBUSH', 'INBOUND_CONQUEST') THEN amount
                    WHEN news_type IN ('INBOUND_LEARN', 'INBOUND_RAZE', 'INBOUND_MASSACRE') THEN 0
                    ELSE -amount
                  END
                ) as acres,
                (CASE WHEN news_type LIKE %(outbound)s THEN 1 ELSE 0 END) as hits_against,
                (CASE WHEN news_type LIKE %(inbound)s THEN 1 ELSE 0 END) as hits_for
            FROM camelot_news_entries
            WHERE news_type LIKE %(inbound)s OR news_type LIKE %(outbound)s
        ) as innerQ
        GROUP BY name, kingdom
        ORDER BY kingdom, net_acres DESC
    """
    results = connection.execute_sql(query, params={'inbound': 'INBOUND_%', 'outbound': 'OUTBOUND_%'})
    json_results = {}
    # import pdb; pdb.set_trace()

    for row in results:
        province = row[0]
        kingdom = row[1]
        acres = row[2]
        hits_against = row[3]
        hits_for = row[4]

        if kingdom not in json_results:
            kingdom_list = []
            json_results[kingdom] = kingdom_list
        else:
            kingdom_list = json_results[kingdom]

        kingdom_list.append({
            'province': province,
            'acres': acres,
            'hits_against': hits_against,
            'hits_for': hits_for,
        })

    return json_results
