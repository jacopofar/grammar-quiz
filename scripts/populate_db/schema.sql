CREATE TABLE languages (
    id       SMALLINT PRIMARY KEY,
    iso693_3 TEXT NOT NULL,
    name     TEXT
);

CREATE TABLE cards (
    from_lang    SMALLINT NOT NULL REFERENCES languages,
    to_lang      SMALLINT NOT NULL REFERENCES languages,
    from_id      INTEGER  NOT NULL,
    to_id        INTEGER  NOT NULL,
    from_txt     TEXT     NOT NULL,
    original_txt TEXT     NOT NULL,
    to_tokens    TEXT[]   NOT NULL
);

CREATE INDEX cards_from_lang_to_lang_index
    ON cards(from_lang, to_lang);
