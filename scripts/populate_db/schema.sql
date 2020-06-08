CREATE TABLE language (
    id       SMALLINT PRIMARY KEY,
    iso693_3 TEXT NOT NULL,
    name     TEXT
);

CREATE TABLE card (
    from_lang    SMALLINT NOT NULL REFERENCES language,
    to_lang      SMALLINT NOT NULL REFERENCES language,
    from_id      INTEGER  NOT NULL,
    to_id        INTEGER  NOT NULL,
    from_txt     TEXT     NOT NULL,
    original_txt TEXT     NOT NULL,
    to_tokens    TEXT[]   NOT NULL,
    PRIMARY KEY (from_id, to_id)
);

CREATE INDEX card_from_lang_to_lang_index
    ON card(from_lang, to_lang);

CREATE TABLE account (
    id INTEGER PRIMARY KEY
);

CREATE TABLE card_user_state(
    from_id    INTEGER                  NOT NULL,
    to_id      INTEGER                  NOT NULL,
    account_id INTEGER                  NOT NULL,
    last_seen  TIMESTAMP WITH TIME ZONE NOT NULL,
    FOREIGN KEY (from_id, to_id) REFERENCES card(from_id, to_id),
    FOREIGN KEY (account_id) REFERENCES account,
    PRIMARY KEY (from_id, to_id, account_id)
);


CREATE TABLE revlog (
    from_id          INTEGER                  NOT NULL,
    to_id            INTEGER                  NOT NULL,
    account_id       INTEGER                  NOT NULL,
    review_time      TIMESTAMP WITH TIME ZONE NOT NULL,
    answers          TEXT[]                   NOT NULL,
    expected_answers TEXT[]                   NOT NULL,
    correct          BOOLEAN                  NOT NULL,
    FOREIGN KEY (from_id, to_id) REFERENCES card(from_id, to_id),
    FOREIGN KEY (account_id) REFERENCES account,
    PRIMARY KEY (from_id, to_id, account_id, review_time)
);

