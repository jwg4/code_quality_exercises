import re


def is_haiku(s):
    return [
        len(
            re.split(
                '\s+',
                re.sub('[aeiouy][^aeiouy ]+', 'X ', t, 0, re.I).strip()
            )
        )
        for t in s.split('\n')
    ] == [5, 7, 5]
