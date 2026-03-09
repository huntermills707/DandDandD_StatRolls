import json

import dash
from dash import html, dcc, Input, Output, State, ALL, ctx

from stats import calculate_roll, calculate_stats
from plots import plot

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dice Pool Probabilities"), 

    # dice store (default 4d6)
    dcc.Store(id='dice-store', data=[{'sides': 6, 'values': [1,2,3,4,5,6]},
                                     {'sides': 6, 'values': [1,2,3,4,5,6]},
                                     {'sides': 6, 'values': [1,2,3,4,5,6]},
                                     {'sides': 6, 'values': [1,2,3,4,5,6]}]),
    # Roll Controls
    html.Div([
        html.Label('Sides:', style={'marginRight': '5px'}),
        dcc.Input(id='new-die-sides', type='number', min=1, max=100, value=6,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Button('Add Die', id='add-die-btn', n_clicks=0,
                    style={'marginRight': '10px'}),
        html.Label('Drop Lowest:', style={'marginRight': '5px'}),
        dcc.Input(id='drop-lowest', type='number', min=0, max=100, value=1,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Label('Drop Highest:', style={'marginRight': '5px'}),
        dcc.Input(id='drop-highest', type='number', min=0, max=100, value=0,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Button('Calculate', id='roll-btn', n_clicks=0, 
                    style={'marginLeft': '20px', 'backgroundColor': '#4CAF50', 
                           'color': 'white'})
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),

    # Stat Controls
    html.Div([
     html.Label('Enable Stat Outcome Calculations:',
                style={'marginRight': '5px', 'font-size': '20px', 'font-weight': 'bold'}),
     dcc.Checklist(id='stat-toggle', options=[''], value=['']),
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),
    html.Div([
        html.Label('Number of Stats:', style={'marginRight': '5px'}),
        dcc.Input(id='n-stats', type='number', min=0, max=10, value=6,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Label('Drop Lowest Stat:', style={'marginRight': '5px'}),
        dcc.Input(id='drop-lowest-stat', type='number', min=0, max=100, value=1,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Label('Drop Highest Stat:', style={'marginRight': '5px'}),
        dcc.Input(id='drop-highest-stat', type='number', min=0, max=100, value=0,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Label('Replace Lowest:', style={'marginRight': '5px'}),
        dcc.Checklist(id='replace-lowest-toggle', options=[''], value=[]),
        dcc.Input(id='replace-lowest-value', min=0, max=100, value=18,
                  style={'width': '60px', 'marginRight': '10px'}),
        html.Label('Replace Highest:', style={'marginRight': '5px'}),
        dcc.Checklist(id='replace-highest-toggle', options=[''], value=[]),
        dcc.Input(id='replace-highest-value', min=0, max=100, value=6,
                  style={'width': '60px', 'marginRight': '10px'}),
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center'}),

    # dice container (visualize dice store)
    html.Div(id='dice-container',
         style={'display': 'grid',
                'gridTemplateColumns': 'repeat(2, 1fr)',
                'gap': '15px',
                'alignItems': 'start'}),

    # roll results display
    html.Div(id='roll-results',
            style={'display': 'grid',
                'gridTemplateColumns': 'repeat(2, 1fr)',
                'gap': '15px',
                'alignItems': 'start'}),

    # modified roll results display
    html.Div(id='roll-mod-results',
            style={'display': 'grid',
                'gridTemplateColumns': 'repeat(2, 1fr)',
                'gap': '15px',
                'alignItems': 'start'}),

    # stat results display
    html.Div(id='stat-results',
            style={'display': 'grid',
                'gridTemplateColumns': 'repeat(1, 1fr)',
                'gap': '15px',
                'alignItems': 'start'}),
])


@app.callback(
    Output('dice-store', 'data'),
    Input('add-die-btn', 'n_clicks'),
    Input({'type': 'remove-die-btn', 'index': ALL}, 'n_clicks'),
    Input({'type': 'sides-input', 'index': ALL}, 'value'),
    Input({'type': 'side-value-input', 'index': ALL, 'side': ALL}, 'value'),
    State('dice-store', 'data'),
    State('new-die-sides', 'value'),
    prevent_initial_call=True
)
def update_dice_store(add_clicks, remove_clicks, sides_values, 
                      side_values, current_data, new_die_sides):
    '''
    function to update the dice pool. Add, drop, mutate, ...

    Parameters:
        add_clicks (bool): trigger to add a die
        remove_clicks (bool): trigger to remove die
        sides_values (int): num sides of new die (not custom)
        side_values (list): list of side values for custom die
        current_data (list): list of current die and data
        new_die_sides (int): change the number of sides in the pool

    Returns:
        current_data (list): updated list of current die and data
    '''
    if not ctx.triggered:
        return current_data

    triggered_id = ctx.triggered_id

    # add die
    if triggered_id == 'add-die-btn':
        sides = new_die_sides if new_die_sides and new_die_sides > 0 else 6
        new_die = {
            'sides': sides,
            'values': list(range(1, sides + 1))
        }
        current_data.append(new_die)
        return current_data

    # remove die
    if (isinstance(triggered_id, dict) and
        triggered_id.get('type') == 'remove-die-btn'):

        index_to_remove = triggered_id['index']
        if 0 <= index_to_remove < len(current_data):
            current_data.pop(index_to_remove)
        return current_data

    # n sides change within die card
    if (isinstance(triggered_id, dict) and
        triggered_id.get('type') == 'sides-input'):

        die_index = triggered_id['index']
        new_sides = ctx.triggered[0]['value']

        if (new_sides is None or
            new_sides < 1 or
            die_index >= len(current_data)):

            return current_data

        old_values = current_data[die_index]['values']

        if len(old_values) < new_sides:
            for i in range(len(old_values), new_sides):
                old_values.append(i + 1)
        else:
            old_values = old_values[:new_sides]

        current_data[die_index]['sides'] = new_sides
        current_data[die_index]['values'] = old_values
        return current_data

    # individual side change
    if (isinstance(triggered_id, dict) and 
        triggered_id.get('type') == 'side-value-input'):

        die_index = triggered_id['index']
        side_index = triggered_id['side']
        new_value = ctx.triggered[0]['value']

        if (0 <= die_index < len(current_data) and 
            0 <= side_index < len(current_data[die_index]['values']) and 
            new_value is not None):

            current_data[die_index]['values'][side_index] = new_value
        return current_data

    return current_data


def render_die(i, die):
    '''
    function to render a die in the dice pool

    Parameters:
        i (int): die id in dice pool
        die (dict): die object
            sides (int): number of sides of a die
            values (list): face values of a die

    Returns:
        out (dash.html.Div): rendered die
    '''
    # build UI to for each side of a die
    side_inputs = [
        dcc.Input(type='number',
                  value=value,
                  id={'type': 'side-value-input', 'index': i, 'side': j},
                  style={'width': '50px', 'textAlign': 'center',
                         'marginRight': '8px', 'marginBottom': '5px'})
        for j, value in enumerate(die['values'])
    ]

    # build die card
    die_card = html.Div([
        # header row
        html.Div([
            html.Strong(f'Die #{i+1}', style={'minWidth': '60px'}),
            html.Div([
                html.Label('Sides:', style={'marginRight': '5px', 
                                            'fontSize': '14px'}),
                dcc.Input(type='number', min=1, max=100, value=die['sides'],
                          id={'type': 'sides-input', 'index': i}, 
                          style={'width': '60px'})
            ], style={'display': 'flex', 'alignItems': 'center',
                      'marginLeft': '20px'}),

            html.Button('×',
                        id={'type': 'remove-die-btn', 'index': i},
                        style={'marginLeft': 'auto', 'color': 'red',
                               'cursor': 'pointer', 'fontSize': '16px'})
        ], style={'display': 'flex', 'alignItems': 'center',
                  'borderBottom': '1px solid #eee', 'paddingBottom': '8px',
                  'marginBottom': '8px'}
        ),

        # side values
        html.Div(side_inputs,
                 style={'display': 'flex', 'flexWrap': 'wrap',
                        'overflowX': 'auto', 'paddingTop': '5px'})
    ], style={'border': '1px solid #ddd', 'borderRadius': '5px', 
              'padding': '12px', 'backgroundColor': '#f9f9f9', 'width': '95%'}
    )
    return die_card


@app.callback(
    Output('dice-container', 'children'),
    Input('dice-store', 'data')
)
def render_dice(dice_data):
    if not dice_data:
        return html.Em("No dice in pool. Click 'Add Die' to start.") 

    dice_elements = []

    for i, die in enumerate(dice_data):
        die_card = render_die(i, die)
        dice_elements.append(die_card)

    return dice_elements


@app.callback(
    Output('roll-results', 'children'),
    Output('roll-mod-results', 'children'),
    Output('stat-results', 'children'),
    Input('roll-btn', 'n_clicks'),
    State('dice-store', 'data'),
    State('stat-toggle', 'value'),
    State('n-stats', 'value'),
    State('drop-lowest', 'value'),
    State('drop-highest', 'value'),
    State('drop-lowest-stat', 'value'),
    State('drop-highest-stat', 'value'),
    State('replace-lowest-toggle', 'value'),
    State('replace-lowest-value', 'value'),
    State('replace-highest-toggle', 'value'),
    State('replace-highest-value', 'value'),
)
def stat_results(n_clicks, dice_data, stat_enable, z, drop_lowest,
                 drop_highest, drop_lowest_stat, drop_highest_stat,
                 replace_lowest_bool, replace_lowest_value,
                 replace_highest_bool, replace_highest_value):
    '''
    function to run rool/stat app Calculations

    Parameters:
        n_clicks (int): trigger to run function
        dice_data (list): die pool
        stat_enable (bool): bool if to run rolls and stats or just stats
        z (int): number of stats
        drop_lowest (int): number of lowest value die to drop from a roll
        drop_highest (int): number of highest values die to drop from a roll
        drop_lowest_stat (int): number of lowest stats to drop
        drop_highest_stat (int): number of highest stats to drop
        replace_lowest_bool (bool): toggle replacing lowest stat
        replace_lowest_value (int): lowest replacement value (if enabled)
        replace_highest_bool (bool): toggle replacing highest stat
        replace_highest_value (int): highest replacement value (if enabled)

    Returns:
        plots (list): list of plots (or None if some are disabled)
    '''
    # exit if malformed
    if not dice_data:
        return html.Div("No dice to roll!", style={'color': 'red'})
    if drop_lowest + drop_highest >= len(dice_data):
        return html.Div("Dropping too many Dice!", style={'color': 'red'})

    # parse dice data, and get roll probabilities
    dice = [die['values'] for die in dice_data]
    roll_probs, roll_cprobs = calculate_roll(dice, drop_lowest, drop_highest)

    # build roll graphs
    fig_rp = dcc.Graph('probs',
                       figure=plot(roll_probs,
                                   title='Roll Probabilities'))
    fig_crp = dcc.Graph('cprobs',
                        figure=plot(roll_cprobs,
                                    title='Cumulative Roll Probailites',
                                    moments=False))

    if not stat_enable:
        return [html.Div(fig_rp, style={'padding': '12px', 'width': '95%'}),
                html.Div(fig_crp, style={'padding': '12px', 'width': '95%'})], \
               None, \
               None

    # get stat probabilities
    stat_probs, roll_probs_mod, roll_cprobs_mod = calculate_stats(
        roll_probs, z, drop_lowest_stat, drop_highest_stat,
        replace_lowest_bool, replace_lowest_value,
        replace_highest_bool, replace_highest_value
    )

    # build stat graphs
    fig_rpm = dcc.Graph('probs_mod', 
                        figure=plot(roll_probs_mod, 
                                    title='Modified Roll Probabilities'))
    fig_crpm = dcc.Graph('cprobs_mod', 
                         figure=plot(roll_cprobs_mod, 
                                     title='Cumulative Modified Roll Probailites', 
                                     moments=False))
    fig_stat = dcc.Graph('stats', 
                         figure=plot(stat_probs,
                                     title='Stat Total Probailites'))

    return [html.Div(fig_rp, style={'paddinging': '12px', 'width': '95%'}),
            html.Div(fig_crp, style={'padding': '12px', 'width': '95%'})], \
           [html.Div(fig_rpm, style={'padding': '12px', 'width': '95%'}),
            html.Div(fig_crpm, style={'padding': '12px', 'width': '95%',})], \
           [html.Div(fig_stat, style={'padding': '12px', 'width': '95%',})]


if __name__ == '__main__':
    app.run(port=8050, host='0.0.0.0')
