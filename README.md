## Dungeon and Dragons Stat Simulator

There are many variations of house rules in regard to stat generation in Dungeons and Dragons.
Each variant has a different effect on how stats are distributed among PCs and NPCs assuming the stats are generated randomly (IE not via point buy). These house rules can have a significant effect on game play because these stats directly effect in game roll modifiers. Some variants may be highly variable, so some PCs could be significantly weaker than others. This could be fun, but it does depend on playstyle.

Another fun option may be giving the PCs the choice of stat generation, but at a cost. For example, if a player chooses a variant that yield lower stats, the DM may assign that PC a random bonus, or if a player chooses a variant with higher yielding stats, the DM may assign that PC a random debuff.

This tool attempts to arm DMs with knowledge of how stats are distributed during stat generation based on different sets of house rules, so DMs can make informed decisions with respect to gameplay. There are two graphics generated:
1. Individual Stat Probabilities: This plots the probability of rolling any given stat (multiply by 100 for percent)
2. Cumulative Stat Probabilities: This plots the probability of the value of all stats added together (multiply by 100 for percent)

Both graphics also include the following statistical measures (not to be confused with character stats):
1. Mean: This is a measure of what the average outcome would be from the stat generation
2. Standard Deviation: This measure how widely results vary. A larger value means it varies more, and a smaller value varies less.
3. Skewness: This measure the shape of the results. Roughly, if the peak of the curve is greater than the mean, the skew is negative, and if the peak of the curve is less than the mean, the skew is negative. In the case where the peak is the mean, the skew is zero.
4. Kurtosis: This measure how the rate of how often values that significantly deviate from the mean occur (outliers). Higher values yield more outliers.

### Theory 

Below is the theory behind how stat statistics are calculated.


#### Metrics

Average

$$ \mu = E[X] = \frac{1}{n}\sum_{i=1}^n X_i $$

Standard Deviation

$$ Var(X) = E\left[\left( X - \mu \right)^2 \right] $$
$$ StandardDeviation = \sqrt{Var(X)} $$

Skewness

$$ Skewness(X) = \frac{E\left[\left( X - \mu \right)^3 \right]}{Var(X)^{3/2}} $$

Kurtosis

$$ Kurtosis(X) = \frac{E\left[\left( X - \mu \right)^4 \right]}{Var(X)^2} $$

#### Individual Stats

When calculating metrics corresponding to individual stats, this code iterates over all possible rolls. Assuming a dice $D$ has $m$ sides where $s(i)$ is the value on the $i^{th}$ side of $D$, a dice can be represented as the following set:
$$ D_i \in \{s_i(1), s_i(2), \dots, s_i(m)\} $$
Now, a specific stat can be represented as an aggregation $f$ of a series of $n$ rolls where dice $D_i$ are each rolled once:
$$ X = \{ f(v_1,v_2,\dots,v_n) : v_i \in D_i \} $$
The number of possible outcomes ($n$):
$$ n = |X| = \prod_{i=1}^n \left|D_i\right| $$
The probability of getting a specific stat can be written as:
$$ p_s(i) = \frac{\sum \mathbf{1}_{\{i\}}(X)}{n} $$
Where $\mathbf{1}_{A}(x) $ the indicator function defined as

$${\displaystyle \mathbf {1} _{A}(x):={\begin{cases}1~&{\text{ if }}~x\in A~,\\0~&{\text{ if }}~x\notin A~.\end{cases}}}$$

Different aggregations are possible. Currently, two aggregations are implemented:
1. Keep all Rolls: $f(X) =\sum X$
2. Drop Lowest m Rolls: $f(X) = \sum X - \sum\min_m X$

#### Cumulative Stats

When calculating cumulative stats
$$ Y = \{ x_0,x_1,\dots,x_z : x_i \in X_i \} $$
Where there are $z$ stats calculated. For D&D, there are 6 stats rolled, but in the case of dropping lowest stats, extra stats must be rolled. In this case, there are $|Y|$ possible outcomes: 
$$ |Y| = n^z$$
In the case of 6 stats with 16 possible values (3-18), there are ~16 million possible outcomes. Too Big! To speed up computer time, itrate over combinations (with replacement).
$$ C_R(n,r) = \left({n \choose r}\right) = \frac{(n+r-1)!}{r!(n-1)!} $$
For 6 stats with 16 possible values, there are 54264 combinations with replacement (better!). 

However, when iterating over combinations, probabilities will need to be adjusted by the permutations for each combination, and roll probabilities of the permutation. With $S$ as the set of all combinations, the number of permutations $h$ can be calculated as:
$$ h(S_i) = n!\prod_{j=1}^n \left( \sum \mathbf{1}_{\{j\}}(S_i) \right) !^{-1} $$
And the probability of specific combination $p_c$ can be calculated as:
$$ p_c(i) = \frac{h(S_i)}{C_R(n,r)} \prod_{\forall j \in S_i} p_s(j) $$

Depending on the number of stats rolled, different filters are possible. Currently, three filters are implemented:
1. Keep all Stats: $g(Y) = Y$
2. Drop Lowest m Stats: $g(Y) = Y - \min_m Y$
3. Replace Lowest Stat with k: $g(Y) = Y - \min Y + \{k\}$

With this, we can now calculate our metrics as:
$$ E[g(Y)] = \sum_{\forall i \in S} p_c(i) \sum g(Y_i)$$

#### Probabilities of Individual Values And Cumulative Stats

Since all probabilities are stored, probabilities of cumulated stats can be calculated by adding the probabilities for all combinations that sum to a specific value.

Additionally, probabilities can be calculated similarly. by adding the probabilities of all combinations containing a roll and normalize for the number of stats in each combination.

These values are plotted.
