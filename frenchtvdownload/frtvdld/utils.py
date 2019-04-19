import random, json
from datetime import datetime

def get_random_string(length = 5):
  s = ""
  for i in range(0, length):
    s = s + chr(random.randint(ord('a'), ord('z')))
  return s

def get_datetime_now_string(dt=None):
  wd = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
  if dt is None:
    d = datetime.now()
  else:
    d = dt
  s = "%d-%02d-%02d_%s" % (d.year, d.month, d.day, wd[d.weekday()])
  return s