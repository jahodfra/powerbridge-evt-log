import glob
import struct
from datetime import datetime
from collections import namedtuple


RECORD_FORMAT = "<IIIIB"
RECORD_SIZE = struct.calcsize(RECORD_FORMAT)
TIME_SHIFT_IN_SECONDS = -3600

Record = namedtuple("Record", "start flags event_id unknown text")
# event_id is not unique (it's just for the same type of event)


def parse_file(path):
  raw = open(path, "rb").read()
  header = raw[:16]
  assert header == b'_evt0\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00', f"Wrong header {header}"
  i = 16
  while i < len(raw):
    ts, flags, event_id, unknown, text_size = struct.unpack(RECORD_FORMAT, raw[i:i+RECORD_SIZE])
    # a seems kind of a bit mask
    start = datetime.fromtimestamp(ts + TIME_SHIFT_IN_SECONDS)
    text = raw[i+RECORD_SIZE:i+text_size+RECORD_SIZE].decode('utf-8')
    yield Record(start, bin(flags), event_id, unknown, text)
    i += text_size + RECORD_SIZE


def parse_eventlog():
  rows = []
  for path in glob.glob("eventlog/EL_*.evt"):
    rows.extend(parse_file(path))
  rows.sort()
  for row in rows:
    if row.flags[-2] == '1':
      # The end event is generated together with the start, i don't know why
      continue
    # print(row.start, row.text.ljust(20), row.flags, row.event_id, row.unknown)
    if row.text == "Signál MaR 50":
      start = row.start
    elif row.text == "Konec signálu MaR 50":
      print(row.start, (row.start - start).seconds)
      


parse_eventlog()
