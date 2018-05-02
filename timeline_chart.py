import pandas as pd
import numpy as np
import datetime as dt
from datetime import timedelta
from collections import OrderedDict
import matplotlib.pyplot as plt
#plt.style.use('bmh')
from Timing_Module import Timing
from Event_Module import IdiosyncraticVol, TakeoutEvent, Earnings, Event
from term_structure import term_structure

def filter_discrete_events(events):
    return [evt for evt in events if not isinstance(evt, (IdiosyncraticVol, TakeoutEvent))]

def get_event_center_dates(events):
    return [Timing(evt.timing_descriptor).center_date for evt in events]

def get_event_mean_moves(events):
    return [evt.get_distribution().mean_move for evt in events]


def get_event_timeline(events: 'list of events' = None, symbol: 'str' = '', expiries = None):
    """Get the Event Timeline in the form of a graph for a list of events. Symbol is an optional parameters to display in the Graph Title"""

    # Establish event information: events, center_dates, mean_moves
    events = filter_discrete_events(events)
    dates = get_event_center_dates(events)
    event_mean_moves = get_event_mean_moves(events)

    # Establish Color Scheme for Scatter Plot. Each unique event type has a different color (e.g. all Earnings events are the same color)
    unique_event_types = set([type(evt) for evt in events])
    color_scheme = OrderedDict([(t[1], t[0]) for t in enumerate(unique_event_types, start=1)])

    # Assign color and size for each scatter point
    event_types = [type(evt) for evt in events]
    scatter_colors = [color_scheme[event_type] for event_type in event_types]
    scatter_sizes = [mean_move*100*50 for mean_move in event_mean_moves] 

    # Instantiate the subplot
    fig, ax1 = plt.subplots(1)

    # Instantiate the Scatter Plot
    # The height of each scatter point is proportional to the event magnitude.
    bar_heights = event_mean_moves
    
    ax1.scatter(dates,
                bar_heights,
                c = scatter_colors,
                marker = 's',
                s = scatter_sizes)
    

    # Set Error Bars for the scatter plot; for now no y_error_bars, although depending on how it looks, I would like to display the magnitude of events scenarios.
    x_error_bars = [Timing(evt.timing_descriptor).timing_duration*.475 for evt in events]
    y_error_bars = [0 for i in range(len(dates))]
    #y_error_bars = [evt.event_width*.475 for evt in events]
    
    ax1.errorbar(dates,
                 bar_heights,
                 xerr = x_error_bars,
                 yerr = y_error_bars,
                 ls='none')
    
    # Create a thin bar graph extending the x-axis to each scatter point to enhance visualization.
    bar_width = .5
    
    ax1.bar(dates,
               bar_heights,
               width = bar_width,
               label = 'Event Mean Move',
               color = 'black'
               #marker='s',
               #s = 250
               )
    
    # Annotate the Scatter Points with the Event Names
    for i in range(len(events)):
        ax1.annotate(s = repr(events[i]),
                     xy = (dates[i], event_mean_moves[i]),
                     xytext = (dates[i], event_mean_moves[i]+.00875 + scatter_sizes[i]*.01*.01*.025),
                     ha='center',
                     fontsize=10.0)


    #fig.autofmt_xdate()
    # Set x and y Tick Marks, Tick Labels, and Axis Labels.
    # Set Tick Marks
    xticks = [dt.date(2018, m, 1) for m in range(dt.date.today().month, 13)]
    ax1.set_xticks(xticks)
    ax1.set_yticks(np.arange(0, max(event_mean_moves)+.05, .05))
    
    # Set Tick Labels
    ax1.set_xticklabels([t.strftime('%-m/%-d/%y') for t in xticks])
    ax1.set_yticklabels(["{:.1f}%".format(y*100) for y in ax1.get_yticks()])
    
    # Set Axis Labels
    ax1.xaxis.label.set_color('darkblue')
    ax1.yaxis.label.set_color('darkblue')
    ax1.title.set_color('saddlebrown')

    # Set Ticks Font Size, tick Rotations, and y-axis Location
    ticks_fontsize = 10.0
    plt.xticks(rotation=45, fontsize = ticks_fontsize)
    plt.yticks(fontsize = ticks_fontsize)
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.tick_right()

    # Set X-Axis Min and Max Dates.
    min_date = min([Timing(evt.timing_descriptor).event_start_date for evt in events])
    max_date = max([Timing(evt.timing_descriptor).event_end_date for evt in events])
    timeD = timedelta(20)
    plt.xlim(min_date - timeD, max_date + timeD)

    # Set Font and Size for x, y Axis Labels and Title
    axis_label_fontsize = 12
    plt.xlabel('Date', fontsize = axis_label_fontsize, fontweight = 'bold')
    plt.ylabel('Event Magnitude', fontsize = axis_label_fontsize, fontweight = 'bold')
    plt.title('{} Event Calendar'.format(symbol), fontsize = axis_label_fontsize*1.5, fontweight = 'bold' )
    
    # Potential options I do not want to use for now. These commands turn off default features.
    """
    ax1.yaxis.set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    """
    
    # For now I don't want to see term structure in the graph, but keeping the code here as an option for later.
    """
    # Create a Line Graph to show Term Structure
    if expiries is not None:
        expiries = [date for date in xticks if date > dt.date.today()]
        term_struc = term_structure(events, expiries, metric = 'IV', mc_iterations = 10**5)
        vols = term_struc.iloc[[term_struc.index.get_loc(1.00, method='nearest')], :].values.tolist()[0]
        print(zip(expiries, vols))
        ax1.plot(expiries,
                 vols,
                 #label = 'Term_Structure',
                 #color = 'black'
                 #marker='s',
                 #s = 250
                 )
        
        ax1.set_yticks(np.arange(0, max(vols)+.05, .05))
    """

    # Set High-Level Graph Parameters; Show Graph
    #ax1.grid(True)
    ax1.title.set_position([.525, 1.025])
    fig.patch.set_facecolor('xkcd:off white')
    ax1.patch.set_facecolor('xkcd:pale grey')
    fig.tight_layout()
    fig.set_size_inches(8, 5)
    plt.legend(loc='best')
    plt.show()

if __name__ == '__main__':
    events = [Event('CRBP', .05, 'Q3_2018'), Earnings('CRBP', .075, 'Q3_2018')]
    get_event_timeline(events)
