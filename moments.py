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


def calculate_moments(probs):
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
