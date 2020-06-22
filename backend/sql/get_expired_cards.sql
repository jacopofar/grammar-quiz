-- retrieves cards for a given user and source/target language
-- there are up to 20 cards never seen by the user
-- and all the cards seen in the past an now expired
SELECT
    c.from_lang,
    c.to_lang,
    c.from_id        AS from_id,
    c.to_id          AS to_id,
    c.from_txt       AS from_text,
    c.to_tokens      AS to_tokens,
    c.original_txt   AS to_text,
    cn.hint          AS hint,
    cn.explanation   AS explanation
FROM
    card c
        JOIN card_user_state cus
             ON c.from_id = cus.from_id
            AND c.to_id = cus.to_id
        LEFT JOIN card_note cn
            ON cus.from_id = cn.from_id
           AND cus.to_id = cn.to_id
           AND cus.account_id = cn.account_id

WHERE
      cus.account_id = $1
  AND cus.next_review < current_timestamp
