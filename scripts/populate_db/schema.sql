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
) PARTITION BY HASH (from_id, to_id);


CREATE TABLE card_h0
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 0);

CREATE TABLE card_h1
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 1);

CREATE TABLE card_h2
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 2);

CREATE TABLE card_h3
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 3);

CREATE TABLE card_h4
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 4);

CREATE TABLE card_h5
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 5);

CREATE TABLE card_h6
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 6);

CREATE TABLE card_h7
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 7);

CREATE TABLE card_h8
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 8);

CREATE TABLE card_h9
    PARTITION OF card
        FOR VALUES WITH (MODULUS 10, REMAINDER 9);

CREATE INDEX card_from_lang_to_lang_index
    ON card(from_lang, to_lang);

CREATE SEQUENCE account_id_seq;

CREATE TABLE account (
    id INTEGER PRIMARY KEY DEFAULT nextval('account_id_seq')
);
-- this is to drop the sequence with the column by default
ALTER SEQUENCE account_id_seq OWNED BY account.id;


CREATE TABLE card_user_state (
    from_id     INTEGER                  NOT NULL,
    to_id       INTEGER                  NOT NULL,
    account_id  INTEGER                  NOT NULL,
    next_review TIMESTAMP WITH TIME ZONE NOT NULL,
    i_factor    SMALLINT,
    ef_factor   REAL,
    FOREIGN KEY (from_id, to_id) REFERENCES card(from_id, to_id) ON DELETE CASCADE,
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
    FOREIGN KEY (from_id, to_id) REFERENCES card(from_id, to_id) ON DELETE CASCADE,
    PRIMARY KEY (from_id, to_id, account_id, review_time)
);

-- users logging in with credentials, not SSO
CREATE TABLE account_internal (
    username      TEXT                     NOT NULL,
    password_hash TEXT                     NOT NULL,
    password_salt TEXT                     NOT NULL,
    creation      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp
) INHERITS(account);

-- anonymous fake user, cannot login
INSERT INTO account_internal(
    username,
    password_hash,
    password_salt
)
VALUES (
    'anonymous',
    'fake',
    'impossible hash'
);

-- users logging in with google
CREATE TABLE account_google (
    mail          TEXT                     NOT NULL,
    creation      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp
) INHERITS(account);

-- report of problem about cards
CREATE TABLE card_trouble (
    from_id     INTEGER                  NOT NULL,
    to_id       INTEGER                  NOT NULL,
    account_id  INTEGER                  NOT NULL,
    ts          TIMESTAMP WITH TIME ZONE NOT NULL,
    description TEXT,
    issue_type  TEXT,
    FOREIGN KEY (from_id, to_id) REFERENCES card ON DELETE CASCADE,
    PRIMARY KEY (from_id, to_id, account_id)
);

-- free-form custom notes about cards
CREATE TABLE card_note (
    from_id     INTEGER                  NOT NULL,
    to_id       INTEGER                  NOT NULL,
    account_id  INTEGER                  NOT NULL,
    ts          TIMESTAMP WITH TIME ZONE NOT NULL,
    hint        TEXT,
    explanation TEXT,
    FOREIGN KEY (from_id, to_id) REFERENCES card ON DELETE CASCADE,
    PRIMARY KEY (from_id, to_id, account_id)
);

-- latest used languages
CREATE TABLE latest_language (
    account_id  INTEGER   NOT NULL PRIMARY KEY,
    src_langs   TEXT[]    NOT NULL,
    tgt_lang    TEXT      NOT NULL
);
