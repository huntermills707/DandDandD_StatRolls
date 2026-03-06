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


def stat_mod(roll, low_drop, high_drop, low_replace, high_replace):
    '''
    Helper function to modify stat roll outcome
    '''
    roll = sorted(roll)
    roll = roll[low_drop:high_drop]
    if low_replace != None:
        roll = [low_replace] + roll[1:]
    if high_replace != None:
        roll = roll[:-1] + [high_replace]
    return roll


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
