
INSERT INTO card_user_state AS cus(
    from_id,
    to_id,
    account_id,
    next_review,
    i_factor,
    ef_factor
    )
VALUES(
     $1,
     $2,
     $3,
     current_timestamp + '1 day' :: INTERVAL,
     1,
     2.65
 )
ON CONFLICT (from_id, to_id, account_id)
DO UPDATE SET
     next_review = current_timestamp + ROUND(cus.i_factor) * '1 day' :: INTERVAL,
     i_factor    = CASE
           WHEN cus.i_factor = 1
               THEN 6
           ELSE round(cus.i_factor * cus.ef_factor) END,
     ef_factor   = GREATEST(1.3, cus.ef_factor + 0.15)
