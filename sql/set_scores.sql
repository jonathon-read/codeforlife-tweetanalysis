INSERT OR REPLACE INTO occurrences(entry_id, frequency)
                VALUES (:entry_id, :frequency +
                                    IFNULL((SELECT frequency
                                              FROM occurrences
                                             WHERE entry_id = :entry_id),
                                           0))
