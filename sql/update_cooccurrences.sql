INSERT OR REPLACE INTO cooccurrences(entry_a, entry_b, frequency)
                VALUES (:entry_a, :entry_b, :frequency +
                                             IFNULL((SELECT frequency
                                                       FROM cooccurrences
                                                      WHERE entry_a = :entry_a AND entry_b = :entry_b),
                                            0))
