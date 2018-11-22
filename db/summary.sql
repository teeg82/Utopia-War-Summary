CREATE TABLE IF NOT EXISTS camelot_news_entries
(
    id serial primary key,
    original_text text NOT NULL,
    news_type VARCHAR(20) NOT NULL,
    originator VARCHAR(100),
    originator_kingdom VARCHAR(8),
    target VARCHAR(100),
    target_kingdom VARCHAR(8),
    amount INTEGER,
    utopia_date VARCHAR(50),
    calculated_date timestamp,
    month_order INTEGER
);


    -- id = AutoField()
    -- original_text = TextField()
    -- news_type = CharField()
    -- originator = CharField()
    -- originator_kingdom = CharField()
    -- target = CharField()
    -- target_kingdom = CharField()
    -- amount = IntegerField()
    -- utopia_date = CharField()
    -- month_order = CharField()
