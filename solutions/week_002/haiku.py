import re


def n_syllables(line):
    stubbed = re.sub('[aeiouy][^aeiouy ]+', 'X ', line, 0, re.I).strip()
    return len(
        re.split('\s+', stubbed)
    )


def is_haiku(poem):
    return [
        n_syllables(line)
        for line in poem.split('\n')
    ] == [5, 7, 5]
