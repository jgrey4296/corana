import csv
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from datetime import date, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


# Setup root_logger:
from os.path import splitext, split
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################


PATH = '/Users/johngrey/github/languageLearning/python/code_analysis/data/csv/police_shootings/fatal-police-shootings-data.csv'

with open(PATH, 'rb') as f:
    text = [x.decode('utf-8','ignore') for x in f.readlines()]

csv_obj = csv.DictReader(text, restkey="remaining", quotechar='"')

rows = [x for x in csv_obj]

keys = [x for x in rows[0].keys()]

with_dates = [(date.fromisoformat(x['date']), x) for x in rows]
with_flattened_dates = [(x.replace(year=2000), y) for x,y in with_dates]

indexed_by_dates = {}
for x,y in with_flattened_dates:
    if x not in indexed_by_dates:
        indexed_by_dates[x] = []
    indexed_by_dates[x].append(y)

counts_dict = {x : len(y) for x,y in indexed_by_dates.items()}
max_shot = max(indexed_by_dates.items(), key=lambda a: len(a[1]))
days_missing = []

a_day = timedelta(days=1)
current = date.fromisoformat("2000-01-01")
for i in range(365):
    if current not in counts_dict:
        days_missing.append(current)
    current += a_day

logging.info("Days Missing in a Year: {}".format(len(days_missing)))

# Load a numpy record array from yahoo csv data with fields date, open, close,
# volume, adj_close from the mpl-data/example directory. The record array
# stores the date as an np.datetime64 with a day unit ('D') in the date column.
paired = [(x,y) for x,y in counts_dict.items()]
sorted_dates = np.argsort([x for x,y in paired])
dates = np.array([paired[x][0].isoformat() for x in sorted_dates], dtype=np.datetime64)
counts = np.array([paired[x][1] for x in sorted_dates])


# first we'll do it the default way, with gaps on weekends
fig, (ax2) = plt.subplots(ncols=1, figsize=(8, 4))

# next we'll write a custom formatter
N = len(dates)
ind = np.arange(N)  # the evenly spaced plot indices


def format_date(x, pos=None):
    thisind = np.clip(int(x + 0.5), 0, N - 1)
    return dates[thisind].item().strftime('%m-%d')


ax2.plot(ind, counts, 'o')
# Use automatic FuncFormatter creation
ax2.xaxis.set_major_formatter(FuncFormatter(format_date))
ax2.set_title("Police Shootings by Day")
fig.autofmt_xdate()

plt.show()
