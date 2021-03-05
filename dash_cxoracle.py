# -*- coding: utf-8 -*-
"""
Purpose:
   This is a Python3 script file for creating, extracting, and plotting data. 
   *** cx_Oracle using a (Oracle 19) database for table functionality. 
   *** Plotly Dash for displaying data in a local web browser.
Author: 
   Ryan Clement
Date:   
   March 2021
"""


# IMPORT
import numpy as np
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
import cx_Oracle as cx


## CREATE: Data
def gaussian(x,mu,sig):
    return  np.exp(-0.5*np.power((x-mu)/sig, 2))

xNum   = 101
xG     = np.linspace(-10,10,xNum)
y1G    = gaussian(xG,0,2)
y2G    = gaussian(xG,-5,2)
y3G    = gaussian(xG,5,2)
xL     = []
yL     = []
yNames = ('m0s2','mN5s2','m5s2')
yDic   = {yNames[0]:y1G, yNames[1]:y2G, yNames[2]:y3G}
for idx in range(xNum):
    xL.append( (idx, xG[idx]) )
for nam in yNames:
    for idx in range(xNum):
        yL.append( (nam, idx, yDic[nam][idx]) )


## OPEN: DB connection
con = cx.connect(
    user="user",
    password="password",
    dsn="ip:port/db_name"
    )


## PRINT: DB & Module Information
print('\n')
print("*** Successfully connected to the Oracle batabase ***")
print('\n')
print('Database version:', con.version)
print('cx_Oracle version:',cx.version)
print('\n')


# ## OPEN: DB cursor
cur = con.cursor()


## CREATE: DB tables
### TABLE: ABSCISSA
try:
    cur.execute("""
                create table abscissa (
                    sample_number INTEGER,
                    value DOUBLE PRECISION,
                    creation_ts timestamp with time zone default current_timestamp,
                    primary key (sample_number)
                    )
                """)
except cx.Error as e:
    errObj, = e.args
    print("Error Code:", errObj.code)
    print("Error Message:", errObj.message)
    print("***** Table ABSCISSA already exists. Skipping table creation. *****\n")
else:
    cur.executemany("insert into abscissa (sample_number, value) values(:1, :2)", xL)
    print(cur.rowcount, "rows inserted into ABSCISSA.")
    con.commit()
### TABLE: ORDINATE
try:
    cur.execute("""
                create table ordinate (
                    gaussian VARCHAR2(5),
                    sample_number INTEGER,
                    value DOUBLE PRECISION,
                    creation_ts timestamp with time zone default current_timestamp,
                    primary key (gaussian,sample_number)
                    )
                """)
except cx.Error as e:
    errObj, = e.args
    print("Error Code:", errObj.code)
    print("Error Message:", errObj.message)
    print("***** Table ORDINATE already exists. Skipping table creation. *****\n")
else:
    cur.executemany("insert into ordinate (gaussian, sample_number, value) values(:1, :2, :3)", yL)
    print(cur.rowcount, "rows inserted into ORDINATE.")
    con.commit()


## QUERY: DB table
xV = []
for row in cur.execute('select value from abscissa'):
    xV.append(row[0])

yV = []
s = "select value from ordinate where gaussian = '{name}'"
# NOTE: If getting name(s) from user perform input validation!
for nam in yNames:
    yTmp = []
    sql = s.format(name=nam)
    for row in cur.execute(sql):
        yTmp.append(row[0])
    yV.append(yTmp)


## CLOSE: DB cursor
cur.close()
## CLOSE: DB connection
con.close()


## PLOT: Data
### CREATE: Figure
fig = go.Figure()
fig.add_trace(
    go.Scatter(x=xV, y=yV[0], name='Gaussian #1', line_color='red')
)
fig.add_trace(
    go.Scatter(x=xV, y=yV[1], name='Gaussian #2', line_color='blue')
)
fig.add_trace(
    go.Scatter(x=xV, y=yV[2], name='Gaussian #3', line_color='purple')
)
fig.update_layout(
    title_text='Database Data',
    xaxis_title_text='Abscissa',
    yaxis_title_text='Ordinate'
    )
### CREATE: App
app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])
### RUN: App
app.run_server(debug=True)
