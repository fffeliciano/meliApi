
from flask import Flask, redirect, url_for, request, render_template
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import dash

from dash import html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

#from buscar_dados import buscar
from app import *
from buscadados import *

from dash_bootstrap_templates import ThemeSwitchAIO
import dash_bootstrap_components as dbc

from dash import dash_table
import dash_auth


# Configuração do Flask
server = Flask(__name__)
server.config.update(
    SECRET_KEY='supersecretkey',
    DEBUG=True
)

# Configuração do Flask-Login
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = '/login'

# Usuários de exemplo
users = {'user': {'password': 'password'}}

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Rotas do Flask
@server.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect('/dashboard')
    return render_template('login.html')

@server.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


# Configuração do Dash
app = dash.Dash(__name__, server=server, routes_pathname_prefix='/dashboard/', external_stylesheets=[dbc.themes.BOOTSTRAP])



#------------------------------------------------------------------------------------------------------------------------------------inicio
# Reading data
df = pd.DataFrame(dados)
#dfcat = pd.DataFrame(category)



df["date_approved_at"] = df["date_approved_at"].apply(lambda d: d.replace(tzinfo=None))
df["Date"] = df["date_approved_at"].dt.date

df["date_approved_at"] = pd.to_datetime(df["date_approved_at"])

df=df.sort_values("date_approved_at")
df=df[df['status'].str.contains('paid')]

df['Date'] = pd.to_datetime(df['date_approved_at']).dt.date
df['paid_amount'] = df['paid_amount'].map(lambda x: float(x))
df['lucro'] = df['lucro'].map(lambda x: float(x))
df['percentual'] = df['percentual'].map(lambda x: float(x))

df['l_positivo'] = df['lucro']
df['l_negativo'] = df['lucro']

df['l_positivo'] = df['lucro'].apply(lambda x: x if x > 0 else 0)
df['l_negativo'] = df['lucro'].apply(lambda x: x if x < 0 else 0)

df = df[df['status'].str.contains('paid')]



#produtos = df[['seller_sku', 'title']].groupby('seller_sku').sum()

produtos = df[['seller_sku','title']].drop_duplicates("seller_sku")


# resumo de lucro_total, lucro posidivo e lucro negativo do dia 
vlr_total = df[['Date', 'lucro',  'l_positivo', 'l_negativo']].groupby('Date').sum('paid_amount')

# valor total faturamento
vlr_faturamento = df[['Date','paid_amount']].groupby('Date').sum('paid_amount')














vendas_sku=df[['seller_sku','lucro']].groupby('seller_sku').sum('lucro').sort_values(by='lucro', ascending=False).head(10)
vendas_sku_negativo=df[['seller_sku','lucro']].groupby('seller_sku').sum('lucro').sort_values(by='lucro', ascending=True).head(10)

mais_vdd_sku=df[['seller_sku','paid_amount']].groupby('seller_sku').sum('paid_amount').sort_values(by='paid_amount', ascending=False).head(10)

#mais_vdd_sku1=df[['seller_sku', 'paid_amount', 'quantity', 'lucro']].groupby('seller_sku').sum(['paid_amount','quantity']).sort_values(by='paid_amount', ascending=False)
mais_vdd_sku1=df[['Date', 'seller_sku', 'paid_amount', 'quantity', 'lucro']].groupby(['Date', 'seller_sku']).sum(['paid_amount','quantity']).sort_values(by='paid_amount', ascending=False)
mais_vdd_sku1['percentual'] = (mais_vdd_sku1['lucro']/mais_vdd_sku1['paid_amount']*100)


# Resetar o índice do primeiro DataFrame para realizar o merge
df1_reset = mais_vdd_sku1.reset_index()

# Realizar o merge
vdd_sku_df = pd.merge(df1_reset, produtos, on='seller_sku', how='left') 

# Redefinir o índice novamente
vdd_sku_df.set_index(['Date', 'seller_sku'], inplace=True)


#mais_vdd_category=df[['category', 'paid_amount', 'lucro', 'quantity']].groupby('category').sum(['paid_amount','lucro','quantity']).sort_values(by='paid_amount', ascending=False).head(10)

# by Faturamento
#mais_vdd_category1 = mais_vdd_category.merge(dfcat, on='category', how='left', indicator=True)
#print(mais_vdd_category1)

# by lucro
#mais_vdd_category_by_lucro = mais_vdd_category1.sort_values(by=['lucro'], ascending=False)
#mais_vdd_category_by_lucro["percentual"] = mais_vdd_category_by_lucro["lucro"]/mais_vdd_category_by_lucro["paid_amount"]*100

# by retorno (melhor percentual de rentabilidade)
#retorno = mais_vdd_category_by_lucro.sort_values(by=['percentual'], ascending=False)

###########################################################################################################
# Lista de produtos com rentabilidade
#df_sku = mais_vdd_sku2[mais_vdd_sku2['lucro'] > 0].sort_values(by='lucro', ascending=False)
#df_sku ['lucro'] =  df_sku['lucro'].map('{:.2f}'.format)

# Lista de produtos com rentabilidade
#df_sorted = mais_vdd_sku2[mais_vdd_sku2['lucro'] > 0].sort_values(by='lucro', ascending=False)
#df_sorted['lucro'] =  df_sorted['lucro'].map('{:.2f}'.format)



###########################################################################################################


"""
mais_vdd_sku4=df[['seller_sku', 'paid_amount', 'quantity', 'lucro']].groupby('seller_sku').sum(['paid_amount','quantity']).sort_values(by='lucro', ascending=True)
mais_vdd_sku4['paid_amount'] = mais_vdd_sku4['paid_amount'].map('{:.2f}'.format)
mais_vdd_sku4['lucro'] = mais_vdd_sku4['lucro'].map('{:.2f}'.format)

"""


#print(vlr_total)

# Styles
tab_card = {'height': '100%'}


config_graph={"displayModeBar": False, "showTips": False}

url_theme1 = dbc.themes.VAPOR
url_theme2 = dbc.themes.FLATLY
template_theme1 = 'vapor'
template_theme2 = 'flatly'

#print(vlr_total.dtypes)
#-----------------------------------------------------------------------------------------------




#-----------------------------------------------------------------------------------------------

# Layout
#============================================================================
#app.layout = dbc.Container([

# Inicialização do aplicativo Dash
#app = dash.Dash(__name__)
# Inicialização do aplicativo Dash com Bootstrap
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    # Row 1
    dbc.Row([
        
        dbc.Col([
            ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            html.H3('Faturamento'),    
            dcc.Dropdown(
                id='date-dropdown',
                #id='date-range',
                options=[
                    {'label': 'Últimos 1 dia', 'value': 1},
                    {'label': 'Últimos 7 dias', 'value': 7},
                    {'label': 'Últimos 15 dias', 'value': 15},
                    {'label': 'Últimos 30 dias', 'value': 30}
                ],
                value=7
            ) 
            
        ], width=12),

        dbc.Col(

            dcc.Graph(id='line-chart-lucro'),
            lg=6
        ),
        dbc.Col(

            dcc.Graph(id='line-chart-faturamento'),
            lg=6
        )
        
    ], className='g-2 my-auto', style={'margin-top': '7px'}),


    # Row 2

    dbc.Row([
        dbc.Col(
            #ThemeSwitchAIO(aio_id='theme', themes=[url_theme1, url_theme2]),
            html.Div([
                #html.Button("Ordenar Lucro", id="sort-button", n_clicks=0),
                # Table Database
                html.Div([
                    dcc.RadioItems(
                        id='table-type',
                        options=[
                            {'label': 'Tabela Completa', 'value': 'full'},
                            {'label': 'Tabela Lucro', 'value': 'lucro'},
                            {'label': 'Tabela Prejuízo', 'value': 'prejuizo'}
                        ],
                        value='full',
                        labelStyle={'display': 'inline-block', 'margin': '10px'}
                    )
                ]),

                dash_table.DataTable(
                    #df.to_dict('records'), [{"order"} for i in df.columns],
                    id='table',


                    columns=[
                        {'name': 'seller_sku', 'id': 'seller_sku', 'type': 'text'},
                        {'name': 'title', 'id': 'title', 'type': 'text'},
                        {'name': 'paid_amount', 'id': 'paid_amount', 'type': 'numeric', "format": {"specifier": "$,.2f"}},
                        {'name': 'quantity', 'id': 'quantity', 'type': 'numeric'},
                        {'name': 'lucro', 'id': 'lucro', 'type': 'numeric', "format": {"specifier": "$,.2f"}},
                        {'name': 'percentual', 'id': 'percentual', 'type': 'numeric', "format": {"specifier": "$,.1f"}}
                    ],

                    #columns=[{"name": i, "id": i} for i in vdd_sku_df.reset_index().columns],
                    sort_action='native',
                    sort_mode='single',
                    page_size= 10,


                    #data=vdd_sku_df.to_dict('records'),
                    #data=valor_sku.reset_index().to_dict('records'),
                    #data=filtered_df.reset_index().to_dict('records'),
                    
                    

                    ### ACERTAR AQUI EM CIMA E NA CALLBACK
                    ### ACERTAR AQUI EM CIMA E NA CALLBACK
                    ### ACERTAR AQUI EM CIMA E NA CALLBACK
                    ### ACERTAR AQUI EM CIMA E NA CALLBACK 
                    
                    
                    
                    #page_size=10,
                    page_action='native',
                    style_table={'overflowX': 'auto'},
                    #style_table={'height': '400px', 'overflowY': 'auto'},
                    style_as_list_view=True,
                    #style_cell={'padding': '5px'},
                    #style_cell={'minWidth': 95, 'maxWidth': 95, 'width': 95,'font_size': '12px','whiteSpace':'normal','height':'auto'},
                    style_cell={
                            'textAlign': 'left',
                            'padding': '10px',
                            'font_family': 'Arial',
                            'font_size': '14px',
                            'backgroundColor': '#1A0933',
                        },
                    style_cell_conditional =[{'if': {'column_id': i},'textAlign': 'left'} for i in ['seller_sku', 'title'] ],
                    #style_header={
                    #        'backgroundColor': 'lightgrey',
                    #        'fontWeight': 'bold'
                    #    },
                    style_header={
                        'backgroundColor': '#1A0933',
                        'fontWeight': 'bold'
                    },

                ),
                
                ]),
        lg=8
        ),

        dbc.Col([
            dcc.Graph(id='indicator1'),
            
        ],lg=2),
        dbc.Col([
            dcc.Graph(id='indicator2'),
            
        ],lg=2),
        
        
    ], className='g-2 my-auto', style={'margin-top': '7px'}),


], fluid=True, className='g-2 my-auto', style={'margin-top': '7px'})
    

# Callback para atualizar o gráfico com base na seleção do usuário

@app.callback(
    [Output('line-chart-lucro', 'figure'),
     Output('line-chart-faturamento', 'figure'),
     Output('table', 'data'),
     Output('indicator1', 'figure'),
     Output('indicator2', 'figure'),

    ],


    [Input('date-dropdown', 'value'),
     Input('table-type', 'value'),
     Input(ThemeSwitchAIO.ids.switch('theme'), 'value')]
    )

##--------------------------------------------------------------------------------------------------------------------------------

##--------------------------------------------------------------------------------------------------------------------------------
def update_graph(selected_value, table_type, toggle):
    template = template_theme1 if toggle else template_theme2
    if selected_value:
        start_date = vlr_total.tail(selected_value - 1)
        start_date_1 = vlr_faturamento.tail(selected_value -1)
        start_date_2 = df.tail(selected_value -1)
        
        filtered_df = start_date
        filtered_df_1 = start_date_1
        valor_vds = start_date_2
    else:
        filtered_df = vlr_total

    

        
    line_lucro = px.line(filtered_df, x=filtered_df.index, y=filtered_df.columns, title='Margem Lucro', template=template)
    fig_faturamento = px.line(filtered_df_1, x=filtered_df_1.index, y=filtered_df_1.columns, title='Faturamento', template=template)
    ##---------------------------------------------------------------------------------------------------------------------------------
    #valor_sku = df[['Date','seller_sku', 'title', 'paid_amount','quantity', 'lucro', 'percentual' ]].groupby('Date').sum('paid_amount')
    valor_sku = valor_vds[['seller_sku', 'title', 'paid_amount', 'quantity', 'lucro', 'percentual' ]].groupby('seller_sku').agg({
        'title': 'first',
        'paid_amount': 'sum',
        'quantity': 'sum',
        'lucro': 'sum',
        'percentual': 'mean'
    })
    valor_sku_6 = valor_sku.reset_index()
    ##---------------------------------------------------------------------------------------------------------------------------------

    valor_sku_4 = valor_vds[['seller_sku', 'title', 'paid_amount', 'quantity', 'lucro', 'percentual' ]].groupby('seller_sku').sum()

    new_vlr_total = vlr_total.iloc[-1]
    new_vlr_faturamento = vlr_faturamento.iloc[-1]
    last_day_lucro = px.line(filtered_df, x=filtered_df.index, y=filtered_df.columns, title='Faturado', template=template)
    last_day_faturamento = px.line(filtered_df, x=filtered_df.index, y=filtered_df.columns, title='Lucro', template=template)


    #vlr_lucro_tt = px.line(filtered_df, x=filtered_df.index, y=filtered_df.columns, title='Margem Lucro', template=template)
    #vlr_lucro = valor_vds['lucro'].sum()


    #dados = last_day_faturamento.to_dict('rows')
    #dados = last_day_faturamento.to_dict('records')
    
    interable = [filtered_df_1['paid_amount'], 10]

    #indicator1 = 120.00
    #indicator2 = 100.00
    
    indicators = []
    
    #interable = ['lucro', 'faturamento']


    
    #for n in interable:
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = 'number',
        title = {'text': 'Lucro'},
        value = valor_vds['lucro'].sum(),
        number = {'prefix': 'R$ ', 'valueformat': ',.2f' },
        delta = {'reference': 160},
        gauge = {
            'axis': {'visible': False}},
        domain = {'row': 0, 'column': 0}))

    fig.update_layout(template=template)

    indicators.append(fig)
    #indicators = fig
    #---------------------------------------------------------------------------

    #fig.update_layout(template=template)
    fig = go.Figure()
    fig.add_trace(go.Indicator(
        mode = 'number',
        title = {'text': 'Faturamento'},
        value = filtered_df_1['paid_amount'].sum(),
        number = {'prefix': 'R$ ', 'valueformat': ',.2f' },
        delta = {'reference': 160},
        gauge = {
            'axis': {'visible': False}},
        domain = {'row': 0, 'column': 0}))

    fig.update_layout(template=template)

    indicators.append(fig)
    #indicators = fig


    #indicators.append(fig)
    #indicator = fig
    
    #---------------------------------------------------------------------------
    
    return line_lucro, fig_faturamento, valor_sku_6.to_dict('records'), indicators[0], indicators[1]


#-----------------------------------------------------------------------------------------------------------------------------------------------
# Callback 2
"""
def last_date(toggle):
    template = template_theme1 if toggle else template_theme2
    new_vlr_total = vlr_total.iloc[-1]
    new_vlr_faturamento = vlr_faturamento.iloc[-1]
    last_day_lucro = px.line(new_vlr_total, x=new_vlr_total.index, y=new_vlr_total.columns, title='Faturamento', template=template)
    last_day_faturamento = px.line(last_day_lucro, x=last_day_lucro.index, y=last_day_lucro.columns, title='Margem de Lucro', template=template)
     
    fig = go.Figure()
    fig.add_trace(go.Indicator(
            mode='number',
            # parei aqui e no video 
            # https://www.youtube.com/watch?v=cYFHqu3UWCk
            # 1:11:50
            
            #title={'text': estado},
            #value=[data.index[-1]]
    ))


    return last_day_lucro, last_day_faturamento
"""


if __name__ == '__main__':
    app.run_server(debug=True)


"""
@app.callback(
    Output('table', 'data'),
    Input('sort-button', 'n_clicks'),
    prevent_initial_call=True
)
def sort_table(n_clicks):
    global mais_vdd_sku4
    # Alternar entre ascendente e descendente baseado no número de cliques
    if n_clicks % 2 == 0:
        df_sorted = mais_vdd_sku4=df[['seller_sku', 'paid_amount', 'quantity', 'lucro']].groupby('seller_sku').sum(['paid_amount','quantity']).sort_values(by='lucro', ascending=True)
        df_sorted['paid_amount'] = df_sorted['paid_amount'].map('{:.2f}'.format)
        df_sorted['lucro'] = df_sorted['lucro'].map('{:.2f}'.format)
    else:
        df_sorted = mais_vdd_sku4=df[['seller_sku', 'paid_amount', 'quantity', 'lucro']].groupby('seller_sku').sum(['paid_amount','quantity']).sort_values(by='lucro', ascending=False)
        df_sorted['paid_amount'] = df_sorted['paid_amount'].map('{:.2f}'.format)
        df_sorted['lucro'] = df_sorted['lucro'].map('{:.2f}'.format)


    return df_sorted.to_dict('records')
"""

