from itertools import product, combinations_with_replacement
from collections import Counter, defaultdict
from math import factorial

from modifiers import drop_interval

def get_rolls(dice, f=sum):
    '''
    Function to get all rolls and apply roll rule f.
    
    Parameters:
        dice (list): list of lists of dice
        f (func): function to aggregate roll
        
    Returns:
        nobs (int): number of observations
        out (list): list of ints of value of each roll
    '''
    nobs = 1
    for die in dice:
        nobs *= len(die)
    return nobs, (f(roll) for roll in product(*dice))


def get_roll_probs(nobs, rolls):
    '''
    Function to calculate probability of each roll
    
    Parameters:
        rolls (list): list of ints for value of each roll
        
    Returns:
        probs (dict): dict of probilities for each roll
    '''
    # Normailze counts by number of observations
    probs = {val:cnt/nobs for val, cnt in Counter(rolls).items()}
    return probs


def calculate_roll(dice, low, high, agg=sum):
    '''
    Function to calculate probability of a specific value for a pool of dice

    Parameters:
        dice (list of list of int/float): input dice pool
        low (int): number of lowest to drop
        high (int): number of higest to drop
        f (function): aggregation function for dice roll instance

    Returns:
        roll_probs (dict of float): probability of a specific value
        roll_cprobs (dict of float): cumlative probability of a specific value
    '''
    # get probs
    high = len(dice) - high
    f = lambda x: drop_interval(x, low, high, agg)
    nobs, rolls = get_rolls(dice, f)
    roll_probs = get_roll_probs(nobs, rolls)

    # get cprobs
    order = sorted(roll_probs.keys())
    roll_cprobs = {order[0]: roll_probs[order[0]]}
    for i in range(len(order)-1):
        i = order[i]
        roll_cprobs[i+1] = roll_cprobs[i] + roll_probs[i+1]
    
    return roll_probs, roll_cprobs
    

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


def calculate_stats(probs, z=6, z_mod=6, f=lambda x: x):
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
    for stats in combinations_with_replacement(span, z_mod):
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
            roll_probs[stat] += c_prob / z
    return stat_probs, roll_probs


def run(n, s, name, dice_agg=sum, 
        stat_adj=0, stat_select=lambda x: x):
        
    nobs, rolls = get_rolls(dice, dice_agg)
    roll_probs = get_roll_probs(nobs, rolls)
    stat_probs, mod_roll_probs = \
        calculate_stats(roll_probs, 6+stat_adj, stat_select)

    return stat_probs, mod_roll_probs
    
