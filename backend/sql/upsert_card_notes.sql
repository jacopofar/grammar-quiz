INSERT INTO card_note (
      from_id,
      to_id,
      account_id,
      ts,
      hint,
      explanation
)
VALUES ($1, $2, $3, current_timestamp, $4, $5)
ON CONFLICT (from_id, to_id, account_id) DO UPDATE SET
   hint = EXCLUDED.hint,
   explanation = EXCLUDED.explanation,
   ts = current_timestamp
