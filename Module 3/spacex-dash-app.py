# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id='site-dropdown',
                                      options=[
                                        {'label': 'All Sites', 'value': 'ALL'},
                                        {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'}, # Placeholder site 1
                                        {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}, # Placeholder site 2
                                        {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},   # Placeholder site 3
                                        {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'}, # Placeholder site 4
                                      ],
                                      value='ALL',
                                      placeholder = 'Select a Launch Site here',
                                      searchable = True
                                      ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # Function decorator to specify function input and output
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                               
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0, max=10000,
                                    step=1000,
                                    # Define marks for better user experience
                                    marks={i: f'{i} Kg' for i in range(0, 10001, 2000)}, # Marks at 0, 2000, 4000, 6000, 8000, 10000
                                    # Set the initial value to cover the full range of data
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    # filtered_df = spacex_df # Ya tienes una copia de spacex_df para trabajar

    if entered_site == 'ALL':
        # Caso 1: ALL sites selected
        # Usar todos los datos para renderizar un gráfico de pastel mostrando el total de
        # lanzamientos exitosos (class=1) por cada sitio.

        # 1. Filtrar solo lanzamientos exitosos (class = 1)
        filtered_df = spacex_df[spacex_df['class'] == 1]
        
        # 2. Crear el gráfico de pastel
        fig = px.pie(
            filtered_df, 
            names='Launch Site', # El nombre de cada porción será el sitio de lanzamiento
            values='class',      # Los valores son el conteo de éxitos (class=1) por sitio
            title='Total Successful Launches by Site'
        )
        return fig
    
    else:
        # Caso 2: Specific site selected
        # Filtrar el DataFrame para incluir solo los datos del sitio seleccionado.
        # Luego, renderizar un gráfico de pastel para mostrar el conteo de Success (class=1) vs. Failed (class=0).

        # 1. Filtrar el DataFrame por el sitio seleccionado
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        
        # 2. Contar las ocurrencias de 'class' (0 y 1)
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'count']
        
        # 3. Crear el gráfico de pastel
        fig = px.pie(
            class_counts,
            values='count',
            names='class', # El nombre será 0 (Failure) y 1 (Success)
            title=f'Total Success Launches for site {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, 
#         `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(entered_site, payload_range):
    """
    Actualiza el gráfico de dispersión basado en el sitio de lanzamiento y el rango de carga útil seleccionados.
    
    :param entered_site: El sitio de lanzamiento seleccionado ('ALL' o específico).
    :param payload_range: Una lista [min_payload, max_payload] del slider.
    :return: Un objeto figura de Plotly para el gráfico de dispersión.
    """
    
    # Filtrar el DataFrame por el rango de Payload seleccionado, independientemente del sitio
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) & 
        (spacex_df['Payload Mass (kg)'] <= high)
    ]
    
    # Lógica If-Else para manejar la selección del sitio
    if entered_site == 'ALL':
        # Caso 1: ALL sites selected
        # Usar el DataFrame filtrado por payload.
        # X=Payload Mass (kg), Y=class, Color=Booster Version Category
        
        fig = px.scatter(
            filtered_df, 
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category', # Color por versión del booster
            title='Correlation between Payload and Success for All Sites'
        )
        return fig
    
    else:
        # Caso 2: Specific site selected
        # Filtrar el DataFrame ya filtrado por payload para incluir solo el sitio seleccionado
        filtered_site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        
        # X=Payload Mass (kg), Y=class, Color=Booster Version Category para el sitio específico
        fig = px.scatter(
            filtered_site_df, 
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}'
        )
        return fig

# Run the app
if __name__ == '__main__':
    app.run()
