from All_Events import sorted_events
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings
from Timing_Module import Timing
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta


events = [evt for evt in sorted_events if not isinstance(evt, (IdiosyncraticVol, TakeoutEvent))]
dates = [Timing(evt.timing_descriptor).center_date for evt in events]
event_mean_moves = [evt.get_distribution().mean_move for evt in events]

color_scheme = {'Earnings': 1, 'Other': 2}

event_types = []
for evt in events:
    if isinstance(evt, Earnings):
        event_types.append('Earnings')
    else:
        event_types.append('Other')

scatter_colors = [color_scheme[event_type] for event_type in event_types]
scatter_sizes = [(mean_move*100)*50 for mean_move in event_mean_moves] 
print(events, dates, event_mean_moves, event_types, sep='\n')

#X = pd.to_datetime(dates)
bar_heights = event_mean_moves
fig, ax1 = plt.subplots(1)
ax1.scatter(dates,
            bar_heights,
            c = scatter_colors,
            marker='s',
            s = scatter_sizes)

error_bars = [timedelta(5) for i in range(len(dates))]
error_bars = [Timing(evt.timing_descriptor).timing_duration*.475 for evt in events]

ax1.errorbar(dates,
             bar_heights,
             xerr = error_bars,
             yerr = [0 for i in range(len(dates))],
             ls='none')

bar_width = .5

ax1.bar(dates,
           bar_heights,
           width = bar_width,
           label = 'Event Mean Move',
           color = 'black'
           #marker='s',
           #s = 250
           )

for i in range(len(events)):
    ax1.annotate(s = repr(events[i]),
                 xy = (dates[i], event_mean_moves[i]),
                 xytext = (dates[i], event_mean_moves[i]+.00875),
                 ha='center',
                 fontsize=10.0)

#fig.autofmt_xdate()
# everything after this is turning off stuff that's plotted by default
"""
ax1.yaxis.set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['left'].set_visible(False)
ax1.spines['top'].set_visible(False)
"""
xticks = [dt.date.today(), dt.date(2018, 7, 1), dt.date(2018, 10, 1), dt.date(2019, 1, 1)]
xticks = dates
xticks = [dt.date(2018, m, 1) for m in [4, 5, 6, 7, 8, 9, 10, 11, 12]]
ax1.set_xticks(xticks)
ax1.set_yticks(np.arange(0, .20, .05))
ax1.xaxis.label.set_color('darkblue')
ax1.yaxis.label.set_color('darkblue')
ax1.title.set_color('brown')
ax1.set_xticklabels([t.strftime('%m/%d/%y') for t in xticks])
ax1.set_yticklabels(["{:.1f}%".format(y*100) for y in ax1.get_yticks()])

axes_fontsize = 10.0
plt.yticks(fontsize = axes_fontsize)
plt.xticks(rotation=45, fontsize = axes_fontsize)
#ax1.xaxis.set_ticks_position('bottom')

#ax1.get_yaxis().set_ticklabels([])
#day = pd.to_timedelta("1", unit='D')
#plt.xlim(X[0] - day, X[-1] + day)

label_fontsize = 11
plt.xlabel('Date', fontsize = label_fontsize, fontweight = 'bold')
plt.ylabel('Event Magnitude', fontsize = label_fontsize, fontweight = 'bold')
#plt.yticks(np.arange(0, .3, .025))
plt.title('NBIX Event Calendar', fontsize = label_fontsize*1.25, fontweight = 'bold' )

#ax1.grid(True)
fig.patch.set_facecolor('xkcd:off white')
fig.tight_layout()
plt.legend()
plt.show()