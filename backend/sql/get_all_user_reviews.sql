SELECT
  rl.from_id,
  rl.to_id,
  rl.review_time,
  rl.answers,
  rl.expected_answers,
  rl.correct,
  c.from_txt,
  c.to_tokens
FROM revlog rl
  JOIN card c
    ON c.from_id = rl.from_id
      AND c.to_id = rl.to_id
WHERE
    account_id = $1
