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
    FOREIGN KEY (account_id) REFERENCES account ON DELETE CASCADE,
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
    FOREIGN KEY (account_id) REFERENCES account ON DELETE CASCADE,
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
