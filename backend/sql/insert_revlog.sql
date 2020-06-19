INSERT INTO revlog (
              from_id,
              to_id,
              account_id,
              review_time,
              answers,
              expected_answers,
              correct
              )
VALUES ($1, $2, $3, current_timestamp, $4, $5, $6)
