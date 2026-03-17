# Dungeon and Dragons Stat Simulator

[![PyCafe](https://py.cafe/logos/pycafe_logo.png)](https://py.cafe/app/huntermills707/dash-dice-roll-probability) <-- PyCafe Demo 


[![render.com](https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSjp6Ur7pViL-Ggg0oJmlXDDTT3IiIbVUpNfQ&s)](https://danddandd-statrolls.onrender.com/) <-- Render Demo (hobby tier -- much slower PyCafe than running locally)

There are many variations of house rules in regard to stat generation in Dungeons and Dragons.
Each variant has a different effect on how stats are distributed among PCs and NPCs assuming the stats are generated randomly (IE not via point buy). These house rules can have a significant effect on gameplay because these stats directly affect in-game roll modifiers. Some variants may be highly variable, so some PCs could be significantly weaker than others. This could be fun, but it does depend on play style.

Another fun option may be giving the PCs the choice of stat generation, but at a cost. For example, if a player chooses a variant that yields lower stats, the DM may assign that PC a random bonus, or if a player chooses a variant with higher yielding stats, the DM may assign that PC a random debuff.

This tool attempts to arm DMs with knowledge of how stats are distributed during stat generation based on different sets of house rules, so DMs can make informed decisions with respect to gameplay. There are two graphics generated:,
1. **Individual Stat Probabilities:** This plots the probability of rolling any given stat (multiply by 100 for percent)
2. **Cumulative Stat Probabilities:** This plots the probability of the value of all stats added together (multiply by 100 for percent)

Plots also display basic descriptive statistics: mean, standard deviation, skewness, and kurtosis.

---

## Installation

```bash
pip install -r requirements.txt
python app.py
```

Then navigate to http://localhost:8051 in your browser.

## Sample Use Cases
1. Classic D&D 4d6 Drop Lowest
   * **Setup:** Add four d6 dice, set "Drop Lowest" to 1
   * **Result:** Average stat ~12.24, standard deviation ~2.85
   * **Use Case:** Standard stat generation for traditional campaigns

2. High-Power Campaign (4d6 Drop 2 Lowest)
  * **Setup:** Add four d6 dice, set "Drop Lowest" to 2
  * **Result:** Average stat ~13.5+, reduced variance
  * **Use Case:** Power fantasy campaigns where players expect strong characters

3. Gritty/Low-Power Campaign (3d6)
  * **Setup:** Add three d6 dice, set "Drop Lowest" to 0
  * **Result:** Average stat ~10.5, higher variance
  * **Use Case:** Hard mode campaigns where character weakness creates tension

4. Custom Dice (Heroic Characters)
  * **Setup:** Add custom dice with weighted values (e.g., d6 with values \[2,3,4,5,6,6\])
  * **Result:** Shifted distribution toward higher values
  * **Use Case:** Starting heroes who already have legendary potential

5. Stat Replacement Rules
  * **Setup:** Enable "Replace Lowest Stat" with value 18
  * **Result:** Guaranteed minimum stat cap
  * **Use Case:** Ensuring no character starts with unusably low stats

6. NPC Generation
  * **Setup:** Configure dice pool matching NPC power level
  * **Result:** Quick probability assessment for encounter balance
  * **Use Case:** Generating consistent stat blocks for recurring NPCs


## DM Preparation Guide
#### Before Session 0

1. **Choose Your Baseline:** Run multiple configurations to compare expected stat totals
2. **Communicate Expectations:** Show players the probability distributions so they understand what "average" means
3. **Set House Rules:** Decide on drop/replace rules and document them

#### Encounter Balancing

1. **Estimate Party Power:** Calculate expected stat total for your chosen method
2. **Compare to Monster Stats:** Use stat totals to gauge CR appropriateness
3. **Adjust Difficulty:** If party stats are consistently high, increase encounter lethality

#### Character Creation Sessions

1. **Run Multiple Methods:** Let players see trade-offs between methods
2. **Point Buy Equivalent:** Use mean stat values to estimate point-buy equivalents
3. **Fairness Checks:** Ensure all players have equal probability distributions

## Game Balancing Insights
#### What the Statistics Tell You

|Metric|What It Means for Balance|
|---|---|
|Mean|Expected average stat value. Higher = more powerful party|
|Std Dev|Variance in outcomes. Higher = more swingy results|
|Skewness|Distribution shape. Negative = more low outliers, Positive = more high outliers|
|Kurtosis|Outlier frequency. Higher = more extreme values (very weak or very strong characters)|

#### Red Flags for Balance Issues
* **High Kurtosis:** Watch for characters with extreme stat spreads
* **Large Std Dev:** Expect significant power gaps between party members
* **Negative Skew:** More characters will fall below average
* **Total Stat Spread >20:** Party may have meaningful mechanical inequality

## Troubleshooting
* "Dropping too many Dice!": Ensure drop count < total dice in pool
* Slow Calculations: Large dice pools with many combinations can take time
* Custom Values: Invalid inputs may cause calculation errors

## MIT License
