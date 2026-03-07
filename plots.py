import plotly.graph_objects as go

from moments import calculate_moments


def plot(probs, title='', moments=True):
    '''
    Function to plot roll probs
    
    Parameters:
        probs (dict): probability of getting a specific roll
    '''

    anno = None
    
    if moments:
        mean, std, skew, kurt = calculate_moments(probs)

        text = [': '.join(x) for x in zip(['Mean', 'STDev', 'Skewness', 'Kurtosis'], 
                                      map(lambda a: "{:.2f}".format(a),[mean, std, skew, kurt]))]
        text = '<br>'.join(text)

        anno = go.layout.Annotation(
            text=text,
            align='left',
            showarrow=False,
            xref='paper',
            yref='paper',
            x=0.00,
            y=1,
            xanchor='left',
            bordercolor='black',
            borderwidth=1,
            borderpad=4
        )


    x = list(probs.keys())
    y = list(probs.values())

    if moments:
        fig = go.Figure(
            data=[
                go.Scatter(x=x, y=y, mode='markers')
            ],
            layout=go.Layout(
                annotations=[
                    anno
                ]
            )
        )
    else:
        fig = go.Figure(
            data=[
                go.Scatter(x=x, y=y, mode='markers')
            ]
        )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=40, b=10),
        xaxis_title='Outcome',
        yaxis_title='Probability',
        title={
            'text': title,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'},
        xaxis = {
            'tickmode': 'linear',
            'tick0': min(x) - min(x)%2,
            'dtick': 1 + (max(x) - min(x)) // 24}
    )

    return fig
