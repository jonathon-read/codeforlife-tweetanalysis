   SELECT frequency
     FROM cooccurrences
LEFT JOIN entries AS entries_a ON entry_a = entries_a.entry_id
LEFT JOIN entries AS entries_b ON entry_b = entries_b.entry_id
    WHERE entries_a.entry = :entry_a AND entries_b.entry = :entry_b
