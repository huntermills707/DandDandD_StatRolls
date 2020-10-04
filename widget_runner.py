from rolls import run, drop_lowest_m, drop_lowest_m_stat, replace_lowest_stat
from ipywidgets import interact_manual, widgets, Layout

def runRoller(n, s, name,
    roll, drop_roll,
    stat, drop_stat, replace_stat):
    
    if roll == 'Drop Lowest Roll':
        dice_agg=lambda x: drop_lowest_m(x, m=drop_roll)
    else:
        dice_agg=sum
        
    if stat == 'Drop Lowest Stat':
        stat_select = lambda x: drop_lowest_m_stat(x, drop_stat)
        stat_adj = drop_stat
    elif stat == 'Replace Lowest Stat':
        stat_select = lambda x: replace_lowest_stat(x, replace_stat)
        stat_adj=0
    else:
        stat_select = lambda x: x
        stat_adj = 0
        
    run(n, s, name, dice_agg, stat_adj, stat_select)
    '''    
    n = [int(val) for val in n.replace(' ', '').split('\n')]
    s = [list(map(int,die.replace(' ', '').split(','))) for die in s.strip().split('\n')]
    dice = get_dice(n, s)
    rolls = get_rolls(dice, dice_agg)
    roll_probs = calculate_roll_probs(rolls)
    stat_probs, mod_roll_probs = \
        calculate_stats(roll_probs, 6+stat_adj, stat_select)

    dice_plot(mod_roll_probs, 'Individual Stats of ' + name)
    
    stat_plot(stat_probs, 'Cumulative Stats of ' + name)
    '''
    
    
def run_widget():
    
    roll = widgets.ToggleButtons(
        options=['Keep All', 'Drop Lowest Roll'],
        value='Drop Lowest Roll',
        description='Roll Modifications:',
        style = {'description_width': 'initial'},
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltips=['', ''],
    )

    drop_roll = widgets.IntSlider(
        value=1,
        min=0,
        max=3,
        step=1,
        description='If Dropping Rolls, How Many?:',
        style = {'description_width': 'initial'},
        layout = Layout(width='50%'),
        disabled=False,
    )

    stat = widgets.ToggleButtons(
        options=['Keep All', 'Drop Lowest Stat', 'Replace Lowest Stat'],
        value='Drop Lowest Stat',
        description='Stat Modifications:',
        style = {'description_width': 'initial'},
        disabled=False,
        button_style='', # 'success', 'info', 'warning', 'danger' or ''
        tooltips=['', ''],
    )

    drop_stat = widgets.IntSlider(
        value=1,
        min=0,
        max=3,
        step=1,
        description='If Dropping Stats, How Many?:',
        style = {'description_width': 'initial'},
        layout = Layout(width='50%'),
        disabled=False,
    )

    replace_stat = widgets.IntSlider(
        value=18,
        min=1,
        max=20,
        step=1,
        description='If Replacing Lowest Stat, With What?:',
        style = {'description_width': 'initial'},
        layout = Layout(width='50%'),
        disabled=False,
    )

    name = widgets.Textarea(
        value='Roll 1d12 + 2d6 Drop Lowest Roll x 7 Drop Lowest Stat',
        placeholder='Type something',
        description='Name of Variant:',
        disabled=False,
        style = {'description_width': 'initial', 'width':'10%'},
        layout = Layout(width='50%')
    )
        
    n = widgets.Textarea(
        value='1\n2',
        placeholder='Type something',
        description='Number of each Dice',
        disabled=False,
        style = {'description_width': 'initial'},
        layout = Layout(width='50%', height='100px')
    )

    s = widgets.Textarea(
        value='1,2,3,4,5,6,7,8,9,10,11,12\n1,2,3,4,5,6',
        placeholder='Type something',
        description='Sides of each Dice ',
        disabled=False,
        style = {'description_width': 'initial', 'width':'10%'},
        layout = Layout(width='50%', height='100px')
    )

    interact_manual(runRoller ,name=name, n=n, s=s,
                    roll=roll, drop_roll=drop_roll,
                    stat=stat, drop_stat=drop_stat, 
                    replace_stat=replace_stat)
    