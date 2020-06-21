-- retrieves cards for a given user and source/target language
-- there are up to 20 cards never seen by the user
-- and all the cards seen in the past an now expired
SELECT
    fl.name        AS from_language,
    tl.name        AS to_language,
    fl.iso693_3    AS from_language_code,
    tl.iso693_3    AS to_language_code,
    c.from_id      AS from_id,
    c.to_id        AS to_id,
    c.from_txt     AS from_text,
    c.to_tokens    AS to_tokens,
    c.original_txt AS to_text
FROM
    card c
        JOIN language fl
             ON fl.id = c.from_lang
        JOIN language tl
             ON tl.id = c.to_lang
        JOIN card_user_state cus
             ON c.from_id = cus.from_id
                 AND c.to_id = cus.to_id
                 AND cus.account_id = $3
                 AND cus.next_review < current_timestamp
WHERE
      fl.iso693_3 = ANY ($2)
  AND tl.iso693_3 = $1
