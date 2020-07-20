SELECT
    substr(date_trunc('day', rl.review_time) :: TEXT, 1, 10)   AS day,
    SUM(CASE WHEN rl.correct THEN 1 ELSE 0 END) AS correct,
    count(1)                                    AS total
FROM revlog rl
WHERE
    account_id = $1
GROUP BY
    date_trunc('day', rl.review_time)
