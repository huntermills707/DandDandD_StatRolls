from itertools import product, combinations_with_replacement
from collections import Counter, defaultdict
from math import factorial

import plotly.graph_objects as go

print("WELCOME TO DUNGEON AND DRAGONS DICE ROLLING")

def get_dice(ns, sidess):
    '''
    Function to return list of lists representing a set of dice
    
    Parameters:
        ns (list): list of ints representing number of each respective dice
        sides (list): lists of lists representing sides of each respective dice
        
    Returns:
        out (list): list of lists of all dice and their sides
    '''
    return [sides for n, sides in zip(ns, sidess) for _ in range(n)]


def get_rolls(dice, f=sum):
    '''
    Function to get all rolls and apply roll rule f.
    
    Parameters:
        dice (list): list of lists of dice
        f (func): function to aggregate roll
        
    Returns:
        out (list): list of ints of value of each roll
    '''
    return [f(roll) for roll in product(*dice)]


def calculate_roll_probs(rolls):
    '''
    Function to calculate probability of each roll
    
    Parameters:
        rolls (list): list of ints for value of each roll
        
    Returns:
        probs (dict): dict of probilities for each roll
    '''
    nobs = len(rolls)
    # Normailze counts by number of observations
    probs = {val:cnt/nobs for val, cnt in Counter(rolls).items()}
    return probs


def get_stat_prob(stats, probs):
    '''
    function to get probabilty for each stat set via cumulative product
    
    Parameters:
        stats (list): list of each of each stat
        
    Returns:
        out (float): probility of getting a stat set
    '''
    out = 1
    for stat in stats:
        out *= probs[stat]
    return out


def get_stat_dup(stats):
    '''
    Function to get number of perumtations for a stat set
    
    Parameters:
        stats (list): list of ints for stat set
    
    Returns:
        dup (int): number of duplicates for a stat combination
    '''
    # calculate maximum number of permutations with replacement
    dup = factorial(len(stats)) 
    
    # reduce number of permutations for repeat values
    cnt = Counter(stats)
    for val in cnt.values():
        dup /= factorial(val)
        
    return dup


def calculate_stats(probs, z=6, f=lambda x: x):
    '''
    Function to calculate stats given roll probabilities, number of stats, and stat rule
    
    Parameters:
        probs (dict): dict of probabilities of getting a rule
        z (int): number of stats rolled
        f (func): function to select rolls
        
    Returns:
        stat_probs (dict): dict of probabilities of getting a stat set (cumulative)
        roll_probs (dict): dict of probabilities of getting a roll
    '''
    # list of possible rolls
    span = list(range(min(probs.keys()), max(probs.keys())+1))
    combo_probs = defaultdict(float)
    
    # iterate over combinations (more efficient that brute force)
    for stats in combinations_with_replacement(span, z):
        # update probability of a combo (combos can repeat with things like drop value)
        combo_probs[tuple(sorted(f(stats)))] += \
            get_stat_prob(stats, probs) * get_stat_dup(stats)
    
    # calcuate overall probabities of rolls and cumulative stats
    stat_probs = defaultdict(float)
    roll_probs = defaultdict(float)
    for stats,c_prob in combo_probs.items():
        stat_sum = sum(stats)
        stat_probs[stat_sum] += c_prob
        for stat in stats:
            # normalize by number of stats
            roll_probs[stat] += c_prob / 6
            
    return stat_probs, roll_probs


def calculate_moment(probs, mean, i):
    '''
    Function to calculate i_th moment
    
    Parameters:
        probs (dict): dict of value and probability
        mean (float): mean of set
        i (int): which moment to calculate
        
    Returns:
        out (float): i_th moment
    '''
    # E[(x - mean)^i]
    return sum(prob*(x-mean)**i for x, prob in probs.items())


def calculate_metrics(probs):
    '''
    Function to calculate roll metrics
    
    Parameters:
        probs (dict): dict of probabilities and values
        
    Returns:
        mean (float): mean of input
        std (float): standard deviation of input
        skew (float): skewness of input
        kurt (float): kurtosis of input
    '''
    mean = sum(prob*x for x, prob in probs.items())
    m_2 = calculate_moment(probs, mean, 2)
    m_3 = calculate_moment(probs, mean, 3)
    m_4 = calculate_moment(probs, mean, 4)
    
    std = m_2**.5
    skew = m_3/m_2**1.5
    kurt = m_4/m_2**2
    
    return mean, std, skew, kurt


def drop_lowest_m(roll, agg=sum, m=1):
    '''
    Helper function to drop lowest value from a roll
    
    Parameters:
        roll (list): list of ints of a roll
        agg (func): function to aggregate roll
        m (int): number of lowest to drop
        
    Returns:
        out (int): value of roll
    '''
    return agg(sorted(roll)[m:])


def drop_highest_m(roll, agg=sum, m=1):
    '''
    Helper function to drop highest value from a roll
    
    Parameters:
        roll (list): list of ints of a roll
        agg (func): function to aggregate roll
        m (int): number of highest to drop
        
    Returns:
        out (int): value of roll
    '''
    return agg(sorted(roll)[:-m])


def drop_lowest_m_stat(stats, m=1):
    '''
    Helper function to drop highest value from a stat set
    
    Parameters:
        stats (list): list of ints of each stat
        agg (func): function to aggregate roll
        m (int): number of highest to drop
        
    Returns:
        out (list): resulting stat set
    '''
    return sorted(stats)[m:]


def replace_lowest_stat(stats, m=18):
    '''
    Helper function to replace lowest stat with an 18
    
    Parameters:
        stats (list): list of ints of each stat
        m (int): value to replace lowest stat with
    '''
    return [m] + sorted(stats)[1:]


def run(n, s, name, dice_agg=sum, 
        stat_adj=0, stat_select=lambda x: x):
        
    n = [int(val) for val in n.replace(' ', '').split('\n')]
    s = [list(map(int,die.replace(' ', '').split(','))) for die in s.strip().split('\n')]
    dice = get_dice(n, s)
    rolls = get_rolls(dice, dice_agg)
    roll_probs = calculate_roll_probs(rolls)
    stat_probs, mod_roll_probs = \
        calculate_stats(roll_probs, 6+stat_adj, stat_select)

    dice_plot(mod_roll_probs, 'Individual Stats of ' + name)
    
    stat_plot(stat_probs, 'Cumulative Stats of ' + name)
    
    
def dice_plot(probs, title=''):
    '''
    Function to plot roll probs
    
    Parameters:
        probs (dict): probability of getting a specific roll
    '''

    mean, std, skew, kurt = calculate_metrics(probs)

    text = [': '.join(x) for x in zip(['Mean', 'STDev', 'Skewness', 'Kurtosis'], 
                                      map(lambda a: "{:.2f}".format(a),[mean, std, skew, kurt]))]
    text = '<br>'.join(text)

    x = list(probs.keys())
    y = list(probs.values())

    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode='markers')
        ],
        layout=go.Layout(
            annotations=[
                go.layout.Annotation(
                    text=text,
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0.00,
                    y=1,
                    xanchor='left',
                    bordercolor='black',
                    borderwidth=1,
                    borderpad=4
                )
            ]
        )
    )

    fig.update_layout(
        autosize=False,
        width=800,
        height=400,
        title={
            'text': title,
            'y':0.8,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis = {
            'tickmode': 'linear',
            'tick0': min(x) - min(x)%2,
            'dtick': 1}
    )

    fig.show()
    
    
def stat_plot(probs, title=''):
    '''
    Function to plot roll probs
    
    Parameters:
        probs (dict): probability of getting a specific stat set (cumulative)
    '''

    mean, std, skew, kurt = calculate_metrics(probs)

    text = [': '.join(x) for x in zip(['Mean', 'STDev', 'Skewness', 'Kurtosis'], 
                                      map(lambda a: "{:.2f}".format(a),[mean, std, skew, kurt]))]
    text = '<br>'.join(text)

    x = list(probs.keys())
    y = list(probs.values())

    fig = go.Figure(
        data=[
            go.Scatter(x=x, y=y, mode='markers')
        ],
        layout=go.Layout(
            annotations=[
                go.layout.Annotation(
                    text=text,
                    align='left',
                    showarrow=False,
                    xref='paper',
                    yref='paper',
                    x=0.00,
                    y=1,
                    xanchor='left',
                    bordercolor='black',
                    borderwidth=1,
                    borderpad=4
                )
            ]
        )
    )

    fig.update_layout(
        autosize=False,
        width=800,
        height=400,
        title={
            'text': title,
            'y':0.8,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis = {
            'tickmode': 'linear',
            'tick0': min(x) - min(x)%2,
            'dtick': 2}
    )

    fig.show()
