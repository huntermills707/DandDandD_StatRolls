import plotly.graph_objects as go

from moments import calculate_moments


# Height of one text line in paper (y) coordinates for a 400px plot.
# 5 lines (1 label + 4 metrics) × this value gives the vertical span of box 1.
_LINE_HEIGHT_PAPER = 0.062


def make_annotation(probs, y_top, label_prefix=''):
    '''
    Build a stats annotation box for a given probs dict.

    Parameters:
        probs        (dict): value → probability mapping
        y_top        (float): paper-y coordinate for the TOP of this box
        label_prefix (str):  bold header line; omitted when empty
    '''
    mean, std, skew, kurt = calculate_moments(probs)
    prefix = f'<b>{label_prefix}</b><br>' if label_prefix else ''
    text = prefix + '<br>'.join(
        f'{k}: {v:.2f}' for k, v in
        zip(['Mean', 'STDev', 'Skewness', 'Kurtosis'], [mean, std, skew, kurt])
    )
    return go.layout.Annotation(
        text=text,
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.00,
        y=y_top,
        xanchor='left',
        yanchor='top',
        bordercolor='black',
        borderwidth=1,
        borderpad=4,
        bgcolor='rgba(255,255,255,0.25)',
    )


def _box1_height(label_prefix):
    '''Return the paper-y height consumed by the first annotation box.'''
    n_lines = 5 if label_prefix else 4   # label line + 4 metrics
    return n_lines * _LINE_HEIGHT_PAPER


def plot(probs, title='', moments=True,
         probs2=None, label1='Base', label2='Modified'):
    '''
    Function to plot roll probs, optionally overlaying a second series.

    Parameters:
        probs  (dict): probability of getting a specific roll (first series)
        title  (str):  plot title
        moments (bool): whether to show stats annotation(s)
        probs2 (dict|None): optional second series to overlay
        label1 (str):  legend label for first series
        label2 (str):  legend label for second series
    '''
    show_legend = probs2 is not None

    x1, y1 = list(probs.keys()), list(probs.values())
    traces = [go.Scatter(x=x1, y=y1, mode='markers',
                         name=label1 if show_legend else '',
                         showlegend=show_legend)]

    annotations = []
    if moments:
        prefix1 = label1 if show_legend else ''
        annotations.append(make_annotation(probs, y_top=1.0,
                                           label_prefix=prefix1))

    if probs2 is not None:
        x2, y2 = list(probs2.keys()), list(probs2.values())
        traces.append(go.Scatter(x=x2, y=y2, mode='markers',
                                 name=label2, showlegend=True))
        if moments:
            # Place box 2 just below box 1
            gap = 0.01
            y2_top = 1.0 - _box1_height(label1) - gap
            annotations.append(make_annotation(probs2, y_top=y2_top,
                                               label_prefix=label2))

    all_x = x1 + (list(probs2.keys()) if probs2 else [])
    fig = go.Figure(
        data=traces,
        layout=go.Layout(annotations=annotations if annotations else [])
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title='Outcome',
        yaxis_title='Probability',
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis={
            'tickmode': 'linear',
            'tick0': min(all_x) - min(all_x) % 2,
            'dtick': 1 + (max(all_x) - min(all_x)) // 24},
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=-0.25,
            xanchor='center',
            x=0.5,
        ) if show_legend else {},
    )

    return fig
