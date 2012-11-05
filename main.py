#!/usr/bin/env python
import random
import csv
from geocode.google import GoogleGeocoderClient
import countryinfo

class Participant(object):
  def __init__(self, row):
    super(Participant, self).__init__()
    self.name = row[1]
    self.nick = row[2]
    geo = GoogleGeocoderClient(False)
    self.address = row[3]
    self.country = None
    self.continent = None
    addr = geo.geocode(self.address)
    if not addr.is_success():
      print "address for %s is not decodable!"%(row[1])
    else:
      for c in addr[0]['address_components']:
        if 'country' in c['types']:
          self.country = c['short_name']
          for country in countryinfo.countries:
            if self.country == country['code']:
              self.continent = country['continent']
    self.suggestions = row[4]
    self.international = not (row[5] == "Nope.")
    self.email = row[6]
    self.giftee = None
    self.gifter = None

  def matched(self):
    return self.gifter is None

  def __str__(self):
    return "%s (%s)"%(self.name, self.continent)

class Matcher(object):
  def __init__(self):
    super(Matcher, self).__init__()
    self._p = []

  @property
  def participants(self):
    return self._p

  def add(self, participant):
    self._p.append(participant)

  @property
  def unmatched(self):
    ret = []
    for p in self._p:
      if not p.gifter:
        ret.append(p)
    return ret

  def generateMatches(self):
    for p in self._p:
      p.giftee = None
      p.gifter = None
    while len(self.unmatched) > 1:
      targets = self.unmatched
      first = random.choice(targets)
      second = random.choice(targets)
      if first == second:
        continue
      if not first.international and not (first.continent == second.continent):
        continue
      first.giftee = second
      second.gifter = first


match = Matcher()
with open('results.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for row in reader:
    p = Participant(row)
    match.add(p)

match.generateMatches()

for p in match.participants:
  print p, '->', p.giftee
