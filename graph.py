import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from Traitement_de_données import calcul_conso
from Traitement_de_données import calcul_temps
from Traitement_de_données import calcul_stops
from Traitement_de_données import temps_arrêt_camembert
from Traitement_de_données import temps_arrêt_barre
from Traitement_de_données import label


def update_Graph(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB, x, y, Type1, options):
    df2 = pd.DataFrame()
    fig_df = pd.DataFrame()

    print(TripnumberB)

    #Si on prend tous les trajets de tous les conducteurs (tout le fichier)
    if 'Tous' in DriverIDA: #Tous les conducteurs
        fig_df = df
        
        #Si on prend tous les conducteurs mais des trajets spécifiques
        if 'Tous' not in TripnumberA:
            for i in TripnumberB:
                df2 = pd.concat([df2, fig_df[fig_df['Tripnumber'] == i]])
            fig_df = df2

    # Si on prend un ou plusieurs conducteurs
    if 'PC' in DriverIDA: 
        for k in DriverIDB:
            fig_df = pd.concat([fig_df,df[df['DriverID'] == k]]) #concaténation du dataframe pour le ou les conducteurs choisis
         
        #Si on ne prend pas tous les trajets des conducteurs en question
        if 'Tous' not in TripnumberA:
            if (Type1 in ['Lignes','Histogramme', 'Boxplot', 'Violon', 'Scatter']) or (options == 'ConsoFuel'):
                for i in TripnumberB:
                    df2 = pd.concat([df2, fig_df[fig_df['Tripnumber'] == i]])
                fig_df = df2

    #Calcul des fonctions pythons (à partir du fichier traitement_de_données.py
    fig_df = calcul_conso(fig_df)
    
    fig_df = calcul_stops(fig_df)
    if x == 'Tripnumber':
        x = fig_df['Tripnumber'].unique()

    if y == 'DuréeTrajet':
        y = calcul_temps(fig_df)

    if y == 'Allure':
        if Type1 == "Barre empilé":
            y = temps_arrêt_barre(fig_df)

        if Type1 == "Camembert":
            y = temps_arrêt_camembert(fig_df)
            fig_df = pd.DataFrame()
            fig_df = fig_df.assign(Allure = y)

    #Plot des graphiques en fonction du type choisi
    if Type1 == "Lignes":
        fig = px.line(fig_df, x = x, y = y, color = options, labels = label())
        
    if Type1 == "Histogramme":
        fig = px.histogram(fig_df, x=x,y=y, color = options, labels = label())

    
    if Type1 == "Boxplot":
        fig = px.box(fig_df, x=x, color = options, labels = label())
        
        
    if Type1 == "Violon":
        fig = px.violin(fig_df, x = x, color = options, labels = label()) 

    if Type1 == "Camembert":
        fig = px.pie(fig_df, names = y, hole = 0.5, labels = label())
        
    if Type1 == "Barplot":
        fig = px.bar(fig_df, x = x, y = y, color = options, labels = label())
        
    if Type1 == "Scatter":
        fig = px.scatter(fig_df, x=x , y=y, color = options, labels = label())
    
    if Type1 == "Barre empilé":
        data = []
        k=0
        noms = ["Normal","Arrêt","Depassement"]

        for i in y:
            data.append(go.Bar(name = noms[k], x = x, y = i))
            k+=1

        fig = go.Figure(data=data)
        fig.update_layout(barmode='stack')

    #Couleur du background
    layout = {'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'}
    #Style du graphique
    template = "plotly_dark"


    #Application des styles sur le graphique
    fig.update_layout(layout, template = template)


    return fig  


def update_Tripnumber_ou_DriverID(df, A, B, type):
    
    options = [{"label": x, "value": x} for x in sorted(df['Tripnumber'].unique()) if str(x) != 'nan']
    print(A)
    print('yesss')
    if A == []:
        valueA = []
        valueB = []
        styleB = {'display': 'none'}
        if type != 'T':
            return options, valueA, valueB, styleB
        return valueA, valueB, styleB


    if 'Tous' == A[-1]:
        valueA = ["Tous"]
        valueB = []
        styleB = {'display': 'none'}
        if type != 'T':
            return options, valueA, valueB, styleB
        return valueA, valueB, styleB

    if A[0] == 'Tous' and len(A) == 2:
        valueA = [A[-1]]
        print(A)
        if A[-1] == 'PC':
            valueB = ['C01']
            c_min_trips = 'N21'
            for driver in B:
                if max(df[df['DriverID'] == c_min_trips]['Tripnumber'].unique()) > max(df[df['DriverID'] == driver]['Tripnumber'].unique()):
                    c_min_trips = driver
 
            options=[{"label": x, "value": x} for x in sorted(df[df['DriverID'] == c_min_trips]["Tripnumber"].unique()) if str(x) != 'nan']
        
        else:
            valueB = ['1']
        styleB = {'display': 'block'}
        
        if type != 'T':
            return options, valueA, valueB, styleB
        return valueA, valueB, styleB
   

    if A != ['Tous']:
        valueA = [A[0]]
        valueB = B
        styleB = {'display': 'block'}
        if A[0] == 'PC':
            c_min_trips = 'N21'
            for driver in B:
                if max(df[df['DriverID'] == c_min_trips]['Tripnumber'].unique()) > max(df[df['DriverID'] == driver]['Tripnumber'].unique()):
                    c_min_trips = driver
    
            options=[{"label": x, "value": x} for x in sorted(df[df['DriverID'] == c_min_trips]["Tripnumber"].unique()) if str(x) != 'nan']
        
        if type != 'T':
            return options, valueA, valueB, styleB
        return valueA, valueB, styleB

