def drop_interval(roll, low=0, high=0, agg=sum):
    '''
    Helper function to drop edges from a roll
 
    Parameters:
        roll (list): list of ints of a roll
        low (int): number of lowest to drop
        high (int): number of higest to drop
        agg (func): function to aggregate roll

    Returns:
        out (int): value of roll
    '''
    return agg(sorted(roll)[low:high])


def stat_mod(stats, low_drop, high_drop, low_replace, high_replace):
    '''
    Helper function to modify stat roll outcome

    Parameters:
        stats (list): list of ints of stats
        low_drop (int): number of lowest stats to drop
        high_drop (int): number of highest stats to drop
        low_replace (int|None): replace lowest stat with val if not None
        high_replace (int|None): replace highest stat with val if not None

    Returns:
        stats (list): list of ints of modified stats
    '''
    stats = sorted(stats)
    stats = stats[low_drop:high_drop]
    if low_replace != None:
        stats = [low_replace] + stats[1:]
    if high_replace != None:
        stats = stats[:-1] + [high_replace]
    return stats
