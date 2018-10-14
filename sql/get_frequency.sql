   SELECT frequency
     FROM occurrences
LEFT JOIN entries USING (entry_id)
    WHERE entry = :entry
