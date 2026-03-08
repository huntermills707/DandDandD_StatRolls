from itertools import product, combinations_with_replacement
from collections import Counter, defaultdict
from math import factorial

from modifiers import drop_interval, stat_mod

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
        probs (dict): dict of probabilities for each roll
    '''
    # Normailze counts by number of observations
    probs = {val:cnt/nobs for val, cnt in Counter(rolls).items()}
    return probs


def get_cprobs(probs):
    '''
    Function to calculate cumulative distribution

    Parameters:
        probs (dict): dict of val:probability pairs

    Returns:
        cprobs (dict): dict of val:cumlative_probability pairs
    '''
    order = sorted(probs.keys())
    cprobs = {order[0]: probs[order[0]]}
    for i in range(len(order)-1):
        i = order[i]
        cprobs[i+1] = cprobs[i] + probs[i+1]
    return cprobs


def calculate_roll(dice, low, high, agg=sum):
    '''
    Function to calculate probability of a specific value for a pool of dice

    Parameters:
        dice (list of list of int/float): input dice pool
        low (int): number of lowest to drop
        high (int): number of higest to drop
        agg (function): aggregation function for dice roll instance

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
    roll_cprobs = get_cprobs(roll_probs)

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


def get_stats(probs, z=6, z_mod=6, f=lambda x: x):
    '''
    Function to get stats given roll probabilities, number of stats, and stat rule

    Parameters:
        probs (dict): dict of probabilities of getting a roll
        z (int): number of stats rolled
        z_mod (int): modified number of stats prior to drops
        f (func): function to select rolls

    Returns:
        stat_probs (dict): dict of probabilities of getting a stat set (cumulative)
        roll_probs_mod (dict): dict of probabilities of getting a roll (modified)
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
    roll_probs_mod = defaultdict(float)
    for stats,combo_prob in combo_probs.items():
        stat_sum = sum(stats)
        stat_probs[stat_sum] += combo_prob
        for stat in stats:
            # normalize by number of stats
            roll_probs_mod[stat] += combo_prob / z
    return stat_probs, roll_probs_mod


def calculate_stats(roll_probs, z,
                    drop_lowest_stat, drop_highest_stat,
                    replace_lowest_bool, replace_lowest_value,
                    replace_highest_bool, replace_highest_value):
    '''
    Function to calculate stat probabilities

    Parameters:
        roll_probs
        z
        drop_lowest_stat
        drop_highest_stat
        replace_lowest_bool
        replace_lowest_value
        replace_highest_bool
        replace_highest_value

    Returns:
        stat_probs
        roll_probs_mod
        roll_cprobs_mod
    '''

    # build stat modification function
    f = lambda x: stat_mod(x,
                           drop_lowest_stat,
                           z + drop_lowest_stat - drop_highest_stat,
                           replace_lowest_value if replace_lowest_bool else None,
                           replace_highest_value if replace_highest_bool else None)
    # determine total stats needed after drops
    z_mod = z + drop_lowest_stat + drop_highest_stat

    # calculate stats
    stat_probs, roll_probs_mod = get_stats(roll_probs, z=z, z_mod=z_mod, f=f)
    roll_cprobs_mod = get_cprobs(roll_probs_mod)
    return stat_probs, roll_probs_mod, roll_cprobs_mod
