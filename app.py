import json

import dash
from dash import html, dcc, Input, Output, State, ALL, ctx

from stats import calculate_roll, calculate_stats
from plots import plot
from theory import theory

# Windows narrower than this (px) switch all plot/dice grids to single-column.
NARROW_WIDTH = 1200

# Initialize Dash app
app = dash.Dash(__name__)
server = app.server

# track window width
app.clientside_callback(
    '''
    function(_trigger) {
        window.addEventListener('resize', function() {
            window.dash_clientside.set_props('window-width', {data: window.innerWidth});
        });
        return window.innerWidth;
    }
    ''',
    Output('window-width', 'data'),
    Input('_page-load', 'children'),
)

# responsive grid styles
app.clientside_callback(
    f'''
    function(win_width) {{
        var narrow = (win_width || 1200) < {NARROW_WIDTH};
        var two_col  = {{display: 'grid', gridTemplateColumns: narrow ? 'repeat(1, 1fr)' : 'repeat(2, 1fr)', gap: '15px', alignItems: 'start'}};
        var one_col  = {{display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)',                              gap: '15px', alignItems: 'start'}};
        return [two_col, two_col, one_col];
    }}
    ''',
    Output('dice-container', 'style'),
    Output('roll-results',   'style'),
    Output('stat-results',   'style'),
    Input('window-width', 'data'),
)

tab1 = dcc.Tab(label='Dice Probabilities', children=[
    # stores
    dcc.Store(id='window-width', data=1200),
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
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center',
              'flexWrap': 'wrap', 'gap': '5px'}),

    # Stat Controls
    html.Div([
        html.Label('Enable Stat Outcome Calculations:',
                   style={'marginRight': '5px', 'font-size': '15px',
                          'font-weight': 'bold'}),
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
    ], style={'marginBottom': '20px', 'display': 'flex', 'alignItems': 'center',
              'flexWrap': 'wrap', 'gap': '5px'}),

    # dice container — style set by clientside callback
    html.Div(id='dice-container'),

    # result plots — style set by clientside callback
    html.Div(id='roll-results'),
    html.Div(id='stat-results'),
])

tab2 = dcc.Tab(label='Theory', children=[
    html.Div([
        dcc.Markdown(theory, mathjax=True)
    ], style={'padding': '15px'})
])

app.layout = html.Div([
    # Hidden div that fires once on page load to seed the window-width store
    html.Div(id='_page-load', style={'display': 'none'}),
    html.H1("Dice Pool Probabilities"),
    dcc.Tabs([tab1, tab2], style={"marginTop": "5px"})
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
        new_die = {'sides': sides, 'values': list(range(1, sides + 1))}
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
        if new_sides is None or new_sides < 1 or die_index >= len(current_data):
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
    side_inputs = [
        dcc.Input(type='number',
                  value=value,
                  id={'type': 'side-value-input', 'index': i, 'side': j},
                  style={'width': '50px', 'textAlign': 'center',
                         'marginRight': '8px', 'marginBottom': '5px'})
        for j, value in enumerate(die['values'])
    ]

    die_card = html.Div([
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
                  'marginBottom': '8px'}),
        html.Div(side_inputs,
                 style={'display': 'flex', 'flexWrap': 'wrap',
                        'overflowX': 'auto', 'paddingTop': '5px'})
    ], style={'border': '1px solid #ddd', 'borderRadius': '5px',
              'padding': '12px', 'backgroundColor': '#f9f9f9', 'width': '95%'})
    return die_card


@app.callback(
    Output('dice-container', 'children'),
    Input('dice-store', 'data'),
)
def render_dice(dice_data):
    if not dice_data:
        return html.Em("No dice in pool. Click 'Add Die' to start.")
    return [render_die(i, die) for i, die in enumerate(dice_data)]


@app.callback(
    Output('roll-results', 'children'),
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
    function to run roll/stat app calculations

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
        roll_children (list): combined base + modified roll plots
        stat_children (list|None): stat total plot, or None if disabled
    '''
    if not n_clicks or not dice_data:
        return None, None
    if drop_lowest + drop_highest >= len(dice_data):
        return html.Div("Dropping too many Dice!", style={'color': 'red'}), None

    # parse dice data and get roll probabilities
    dice = [die['values'] for die in dice_data]
    roll_probs, roll_cprobs = calculate_roll(dice, drop_lowest, drop_highest)

    gs = {'width': '95%'}       # graph fills its grid cell
    ds = {'padding': '12px', 'width': '100%', 'minWidth': 0}  # wrapper

    if not stat_enable:
        fig_rp  = dcc.Graph('probs',  figure=plot(roll_probs,
                                                   title='Roll Probabilities'),
                             responsive=True, style=gs)
        fig_crp = dcc.Graph('cprobs', figure=plot(roll_cprobs,
                                                   title='Cumulative Roll Probabilities',
                                                   moments=False),
                             responsive=True, style=gs)
        return ([html.Div(fig_rp,  style=ds),
                 html.Div(fig_crp, style=ds)],
                None)

    # get stat probabilities
    stat_probs, roll_probs_mod, roll_cprobs_mod = calculate_stats(
        roll_probs, z, drop_lowest_stat, drop_highest_stat,
        replace_lowest_bool, replace_lowest_value,
        replace_highest_bool, replace_highest_value
    )

    # Pair 1: base roll probs + modified roll probs overlaid
    fig_rp = dcc.Graph('probs', figure=plot(
        roll_probs,
        title='Roll Probabilities',
        probs2=roll_probs_mod,
        label1='Base Roll',
        label2='Modified Roll',
    ), responsive=True, style=gs)

    # Pair 2: cumulative base + cumulative modified overlaid
    fig_crp = dcc.Graph('cprobs', figure=plot(
        roll_cprobs,
        title='Cumulative Roll Probabilities',
        moments=False,
        probs2=roll_cprobs_mod,
        label1='Base Roll',
        label2='Modified Roll',
    ), responsive=True, style=gs)

    # Chart 3: stat totals
    fig_stat = dcc.Graph('stats', figure=plot(
        stat_probs,
        title='Stat Total Probabilities',
    ), responsive=True, style=gs)

    return ([html.Div(fig_rp,  style=ds),
             html.Div(fig_crp, style=ds)],
            [html.Div(fig_stat, style=ds)])


if __name__ == '__main__':
    app.run(debug=False, threaded=True, port=8050)
