#!/usr/bin/env python
import sys
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
    self._gifters = {}
    self._giftees = {}
    self._best = 0

  def add(self, participant):
    self._p.append(participant)

  @property
  def participants(self):
    return self._p

  def matched(self):
    ret = []
    for p in self._p:
      if p.gifter and p.giftee:
        ret.append(p)
    return ret

  def unmatchedGiftees(self, iter=-1):
    if iter == -1:
      iter = self._best
    ret = []
    for p in self._p:
      if p not in self._giftees[iter]:
        ret.append(p)
    return ret

  def unmatchedGifters(self, iter=-1):
    if iter == -1:
      iter = self._best
    ret = []
    for p in self._p:
      if p not in self._gifters[iter]:
        ret.append(p)
    return ret

  def unmatched(self, iter=-1):
    return self.unmatchedGiftees(iter)+self.unmatchedGifters(iter)

  def generateMatches(self, maxIters = 50):
    iters = 0
    self._gifters = {}
    self._giftees = {}
    iter = -1
    while iter < maxIters:
      iter += 1
      self._gifters[iter] = {}
      self._giftees[iter] = {}
      subiter = 0
      while len(self.unmatchedGifters(iter)) > 1 and len(self.unmatchedGiftees(iter)) > 1 and subiter < 10:
        subiter += 1
        first = random.choice(self.unmatchedGifters(iter))
        second = random.choice(self.unmatchedGiftees(iter))
        if first == second:
          continue
        if not first.international and not (first.continent == second.continent):
          continue
        self._gifters[iter][first] = second
        self._giftees[iter][second] = first
        subiter -= 1

    self._best = 0
    for i in range(0, iter):
      unmatchCount = len(self.unmatchedGifters())
      if self._best == -1 or unmatchCount < self._best:
        self._best = i
    for gifter, giftee in self._gifters[self._best].iteritems():
      gifter.giftee = giftee
      giftee.gifter = gifter

match = Matcher()
for f in sys.argv[1:]:
  with open(f, 'r') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
      p = Participant(row)
      match.add(p)

match.generateMatches()

print "Matches:"
for p in match.matched():
  print "\t", p, '->', p.giftee

print "UNMATCHED:"
for p in match.unmatched():
  print "\t", p

print "Patially Matched:"
for p in match.unmatchedGiftees()+match.unmatchedGifters():
  print "\t", p.gifter, '->', p, '->', p.giftee
