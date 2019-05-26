lambda s:[len(split('\s+',sub('[aeiouy][^aeiouy ]+','X ',t,0,I).strip()))for t in s.split('\n')]==[5,7,5]
from re import*