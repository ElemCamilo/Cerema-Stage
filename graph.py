import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
import plotly.express as px

from keplergl import KeplerGl
from sklearn.decomposition import PCA
from Config import Configuration
from Traitement_de_données import temps_arrêt_camembert, temps_arrêt_barre, label, variables, max_trip



# Par la suite on utilisera DriverIDA, DriverIDB, TripnumberA, TripnumberB
# à plusieures réprises, c'est pour ça qu'on va expliquer ce que
# c'est chaque variable.
# 
# DriverIDA: liste avec le niveau d'agrégation qu'on veut avoir, soit Tous soit Par Conducter(PC)
# DriverIDB: liste des conducteurs chosis 
# TripbumberA: liste avec le niveau d'agrégation qu'on veut avoir, soit Tous soit Par Trajet(PR)
# TripbumberB: liste des trajets chosis 



def filtrage_dataframe_Trajet(df,TripnumberA,TripnumberB):                                         # Filtrage du dataframe par trajet                                  
    df2 = pd.DataFrame()

    if 'Tous' not in TripnumberA:                                                                  # Si on ne choisit pas tous les trajets
        for i in TripnumberB:
            df2 = pd.concat([df2, df[df['journey_uuid'] == i]])                                    # On crée un dataframe avec les trajets choisis

    else:   
        df2 = df                                                                                   # Si on choisit tous les trajets                                                                                
    return df2



def filtrage_dataframe_conducteur(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB):               # Filtrage du dataframe par trajet et par conducteur 
    vitesse, temps, limite, Conducteur, Trajet, Longitude, Latitude, pente, conso, gear, DistanceCum, Acceleration, smoothed_acceleration, temps_min2, SystemType = variables(df_config)
    
    df2 = pd.DataFrame()
    fig_df = pd.DataFrame()

    if 'Tous' in DriverIDA:                                                                        # Si on prend tous les conducteurs 
        fig_df = df
        
    if 'PC' in DriverIDA:                                                                          # Si on prend un ou plusieurs conducteurs
        for k in DriverIDB:                                                                        
            fig_df = pd.concat([fig_df,df[df[Conducteur] == k]])                                   # Concaténation du dataframe pour le ou les conducteurs choisis
         
    if 'Tous' not in TripnumberA:                                                                  # Si on ne prend pas tous les trajets des conducteurs en question
        for i in TripnumberB:
            df2 = pd.concat([df2, fig_df[fig_df[Trajet] == i]])                                    # Concaténation du dataframe pour le ou les trajets choisis
        fig_df = df2
    else:
        c_min_trips = max_trip(df)                                                                 # On retourne le/un des DriverID qui a le numéro de trajet le plus grand
        for driver in DriverIDB:                                                                   # On cherche à afficher les trajets que tous les conducteurs ont en commun, pour cela on prend le nombre de trajets de celui qui en a le moins
            if max(df[df[Conducteur] == c_min_trips][Trajet].unique()) > max(df[df[Conducteur] == driver][Trajet].unique()):       # Si le trajet le plus grand du conducteur qui a le moins par l'instant est supérieur au plus grand d'un des conducteur choisis (ex : 4 > 3, 4 et 3 étant des numéros de trajet)      
                c_min_trips = driver                                                                                                           # On change le conducteur qui a le trajet le plus grand
        fig_df = fig_df[fig_df[Trajet] <= max(fig_df[fig_df[Conducteur] == c_min_trips][Trajet].unique())]                         # On choisit les trajets communs des conducteurs
                                                                                                                                              
    return fig_df

def filtrage_dataframe(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB):                          # Si on ne dispose pas du conducteur mais que du trajet, on lance la première fonction
    if DriverIDB == [None] :
        return filtrage_dataframe_Trajet(df,TripnumberA,TripnumberB)
    else:
        return filtrage_dataframe_conducteur(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB)


def update_map(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB):                                  # Fonction qui met à jour la map Kepler
    map_df = filtrage_dataframe(df, DriverIDA, DriverIDB, TripnumberA,TripnumberB)                 # On filtre les données pour avoir celles qui nous intéressent pour la map
    map_1 = KeplerGl(data={"DATA": map_df}, config = Configuration())                              # On définit la map. On utilise une configuration qu'on définit pour ajouter les icônes et les points directement sur la map et pas manuellement, c'est à dire en le choisissant sur Kepler 
    map_1.save_to_html(file_name="map.html", center_map = True)                                    # On sauvegarde la map dans un fichier html
    return open("map.html").read()                                                                 # On retourne le fichier html crée

def update_Graph(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB, x, y, Type1, options):          # Fonction qui permet de mettre à jour les graphiques
    if x != []:
        x = x[-1]
    if y != []:
        y = y[-1]                                                                                  # Si plusieurs choix d'axes/types/options ont été choisi, on garde les derniers sélectionnés
    if Type1 != []: 
        Type1 = Type1[-1]
    if options != []:
        options = options[-1]
    

    fig_df = filtrage_dataframe(df, DriverIDA,DriverIDB, TripnumberA,TripnumberB)                  # Filtrage des données
          
    
    styleX = {'display': 'block'}                                                                  # Style de X
    styleY = {'display': 'block'}                                                                  # Style de Y
    styleO = {'display': 'block'}                                                                  # Style des options


                                                                                                   # Plot des graphiques en fonction du type choisi
    if Type1 == "Lignes":
        fig = px.line(fig_df, x = x, y = y, color = options, labels = label())
        
    if Type1 == "Histogramme":
        fig = px.histogram(fig_df, x=x,y=y, color = options, labels = label())

    
    if Type1 == "Boxplot":
        styleY = {'display': 'none'}                                                               # On enlève la posibilité de cliquer sur Y car la seule valeur qui intéresse c'est celle de X 
        fig = px.box(fig_df, x=x, color = options, labels = label())
        
        
    if Type1 == "Violon":
        styleY = {'display': 'none'} 
        fig = px.violin(fig_df, x = x, color = options, labels = label()) 

    if Type1 == "Camembert":
        styleX = {'display': 'none'}                                                               # On enlève la posibilité de cliquer sur X car la seule valeur qui intéresse c'est celle de Y
        styleO = {'display': 'none'}                                                               # On ne peut pas cliquer sur Options car plotly il definit les couleurs automatiquement

        if y == 'Allure':
            y_fig = temps_arrêt_camembert(fig_df)                                                  
            fig_df = pd.DataFrame()
            fig_df = fig_df.assign(Allure = y_fig)
            fig = px.pie(fig_df, names = y_fig, hole = 0.5, labels = label())
        else:
            fig = px.pie(fig_df, names = y, hole = 0.5, labels = label())
    if Type1 == "Barplot":
        fig = px.bar(fig_df, x = x, y = y, color = options, labels = label())
        
    if Type1 == "Scatter":
        fig = px.scatter(fig_df, x=x , y=y, color = options, labels = label())
    
    if Type1 == "Barre empilé":
        x = 'Tripnumber'                                                                 
        y = 'Allure'                                                                               # On prend ses x et y là car c'est les seules avec lesquelles on peut faire une barre empilé 
        x_fig = fig_df['Tripnumber'].unique()
        y_fig = temps_arrêt_barre(fig_df)
        data = []
        k=0
        noms = ["Respet","Arrêt","Depassement"]

        styleO = {'display': 'none'}                                                               # On ne peut pas cliquer sur Options car plotly il definit les couleurs automatiquement

        for i in y_fig:
            data.append(go.Bar(name = noms[k], x = x_fig, y = i))
            k+=1

        fig = go.Figure(data=data)
        fig.update_layout(barmode='stack')

    layout = {'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'}              # Couleur du background          
    template = "plotly_dark"                                                                       # Style du graphique

    fig.update_layout(layout, template = template)                                                 # Application des styles sur le graphique

    return fig, [x], styleX, [y], styleY, [options], styleO, [Type1] 


def update_Tripnumber_ou_DriverID(df, df_config,  A, B, type):                                     # Fonction qui permet la mise à jour des options de conducteur et de trajet. A et B peuvent être resp. DriverIDA et DriverIDB soit resp. TripnumberA et TripnumberB  
    vitesse, temps, limite, Conducteur, Trajet, Longitude, Latitude, pente, conso, gear, DistanceCum, Acceleration, smoothed_acceleration, temps_min2, SystemType = variables(df_config)
    options = [{"label": x, "value": x} for x in sorted(df[Trajet].unique()) if str(x) != 'nan']   # On prend dans l'ordre les trajets qu'il y a dans le dataframe
    if A == []:                                                                                    # Si on ne choisit pas ce qu'on veut comme niveau d'agrégation des conducteurs/trajets:
        valueA = []                                                                                #    - La valeur de A devient la liste vide
        valueB = []                                                                                #    - La valeur de B devient la liste vide
        styleB = {'display': 'none'}                                                               #    - On enlève la possiblité de cliquer sur B et alors de choisir des conducteurs/trajets
    
    if A[-1] == 'Tous':                                                                            # Si on choisit tous comme niveau d'agrégation:
        valueA = ["Tous"]                                                                          #    - La valeur devient Tous. On fait ça car dans le cas où il y aurait plusieurs choix, on prend toujours le dernier choix qui a été fait
        valueB = []                                                                                #    - On set la valeur de B a la liste vide car il n'y a pas besoin de choisir des conducteurs/trajets
        styleB = {'display': 'none'}                                                               #    - On enlève la possiblité de cliquer sur B et alors de choisir des conducteurs/trajets
        c_min_trips = max_trip(df)
        if A[-1] == 'PC':                                                                          # Si le dernier choix de A a été Par Conducteur
            for driver in [x for x in sorted(df[Conducteur].unique()) if str(x) != 'None']:        # On parcours une liste avec tous les conducteurs
                if max(df[df[Conducteur] == c_min_trips][Trajet].unique()) > max(df[df[Conducteur] == driver][Trajet].unique()):
                    c_min_trips = driver
                    
        options=[{"label": x, "value": x} for x in sorted(df[df[Conducteur] == c_min_trips][Trajet].unique()) if str(x) != 'nan']    # On prend les trajets du conducteur qui en a le moins 

    if A[-1] != 'Tous':
        valueA = [A[-1]]
        valueB = B
        styleB = {'display': 'block'}
        c_min_trips = max_trip(df)
        if A[-1] == 'PC':
            for driver in B:
                if max(df[df[Conducteur] == c_min_trips][Trajet].unique()) > max(df[df[Conducteur] == driver][Trajet].unique()):
                    c_min_trips = driver
        options=[{"label": x, "value": x} for x in sorted(df[df[Conducteur] == c_min_trips][Trajet].unique()) if str(x) != 'nan']
        

    if type == 'T':                                                                                # T pour savoir si les A et B correspondent a des trajets ou des conducteurs (Tripnumber ou DriverID)
        return options, valueA, valueB, styleB
    return valueA, valueB, styleB            
                


def ACP(df, columns):
    layout = {'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'}   #style
    template = "plotly_dark"

    # Tableau récapitulatif, avec les variances expliquées, les proportions de variance expliquée simples et cumulées
    df2 = df[columns]
    X = (df2-df2.min())/(df2.max()-df2.min())

    pca = PCA(n_components=len(columns))
    components = pca.fit_transform(X)
    eig = pd.DataFrame(
    {
    "Dimension" : ["Dim" + str(x + 1) for x in range(len(columns))], 
    "Variance expliquée" : pca.explained_variance_,
    "% variance expliquée" : np.round(pca.explained_variance_ratio_ * 100),
    "% cum. var. expliquée" : np.round(np.cumsum(pca.explained_variance_ratio_) * 100)
    }
    )
    fig_val_prop = px.bar(eig, x = "Dimension", y = "% variance expliquée", text = columns) # permet un diagramme en barres
    fig_val_prop.update_layout(layout, template = template)

    if len(columns) >= 3:
        return ACP3D(df, columns), fig_val_prop

    else:     
    # Histogramme des valeurs propres
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
        fig1 = px.scatter(components, x=0, y=1, text = df['names'], title = 'ACP', color = df['SystemType'])
        for i, feature in enumerate(columns):
            fig1.add_shape(
                type='line',
                x0=0, y0=0,
                x1=loadings[i, 0],
                y1=loadings[i, 1]
            )
            fig1.add_annotation(
                x=loadings[i, 0],
                y=loadings[i, 1],
                ax=0, ay=0,
                xanchor="center",
                yanchor="bottom",
                text=feature,
            )
        fig1.update_layout(layout, template = template)
        fig1.update_traces(textposition='top center')
        
        #style des figures (mode obscur)
        return fig1, fig_val_prop


def update_agrege(df, df_config, X, Variable_quali):
    
    vitesse, temps, limite, Conducteur, Trajet, Longitude, Latitude, pente, conso, gear, DistanceCum, Acceleration, smoothed_acceleration, temps_min2, SystemType = variables(df_config)
    
    ## Partie ANOVA
     
    df.to_csv('fichier_donnes.csv', header=True, columns = [X[-1]]+Variable_quali, index=False, sep=',')     # Création du fichier qui va être lu dans le script R

    os.chdir("C:/Program Files/R/R-4.1.2/bin")                                        
    os.system('Rscript.exe C:/Users/camal/Documents/Stage_Cerema/Donnees/script_R.R')                        # Route où se trouve notre script R et lancement du script R (ANOVA)
    os.chdir("C:/Users/camal/Documents/Stage_Cerema/Donnees/")

    with open('data_ex_export.txt') as anova:                                                                 # Transformation du fichier texte obtenu en html
        lines = anova.readlines()                                                                             # Liste contenant les lignes du fichier
        df_anova = pd.DataFrame({'Anova': lines})                                                             # Pour le faire Vectoriellement et alors beaucoup plus rapidement
        df_anova = '<pre>'+ df_anova + '</pre>'
        text_file = open("ANOVA.html", "w")
        text_file.write("<pre><h1>Anova</h1></pre>")   
        text_file.write("<style>pre{color: white;}</style>")                                                  # Pour changer la couleur du texte en blanc
                              
        for i in range(len(df_anova['Anova'])):
            liste = list(df_anova['Anova'][i])
            if liste != ['<', 'p', 'r', 'e', '>', '\n', '<', '/', 'p', 'r', 'e', '>']:                        # Pas besoin d'avoir des espaces en plus entre les lignes, raison du pourquoi on prend pas en compte les listes de ce type là 
                for j in range(len(liste)):
                    text_file.write(liste[j])
            
    text_file.close()                                                                                         # On sauvegarde le fichier ANOVA.html qui contient l'anova faite par R


    # boxplot pour Anova

    df_agrege_conducteur = df.groupby([Conducteur, Trajet]).mean() #groupby sur les conducteurs et les trajets
    df_agrege_conducteur = df_agrege_conducteur.reset_index()
    df_agrege_conducteurf = df[[SystemType,Conducteur, Trajet]].groupby([Conducteur, Trajet]).first() #groupby sur les conducteurs et les trajets
    df_agrege_conducteurf = df_agrege_conducteurf.reset_index()
    df_agrege = df_agrege_conducteur.merge(df_agrege_conducteurf)


    fig = px.box(df_agrege[[Variable_quali[-1], X[-1]]], x = Variable_quali[-1], y = X[-1], labels = label())
    layout = {'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'}   #style
    template = "plotly_dark"
    fig.update_layout(layout, template = template)


    return open('ANOVA.html').read(), fig, [X[-1]]



def ACP3D(df,columns):
    df_agrege = df
    df_agrege['SystemType2'] = df['SystemType'].replace('SS',0 )
    df_agrege['SystemType2'] = df_agrege['SystemType'].replace('AS',1 )

    df2 = df_agrege[columns]
    X = (df2-df2.min())/(df2.max()-df2.min())

    pca = PCA(n_components=len(columns))
    components = pca.fit_transform(X)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    components = pd.DataFrame(components)
    trace_liste = []

    for i in df_agrege['SystemType'].unique():
        print(i)
        df_agregeV = df_agrege[df_agrege['SystemType'] == i]

        trace1 = go.Scatter3d(
            x=components[0],
            y=components[1],
            z=components[2],
            mode='markers',
            text = list(df_agregeV['names']),
            name = i,
            marker=dict(
                size=2,
                color= list(df_agregeV['SystemType']),           # set color to an array/list of desired values
                colorscale = 'Viridis',

        )
        )

        trace_liste.append(trace1)

    for i, feature in enumerate(columns):
        trace_liste.append(go.Scatter3d(
            x=[0,loadings[i,0]],
            y=[0, loadings[i,1]],
            z =[0, loadings[i,2]],
            mode='lines',
            name = feature,
            marker=dict(size=20),)
        
    )
    fig = go.Figure(data= trace_liste)
    layout = {'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)'}   #style
    template = "plotly_dark"
    fig.update_layout(layout, template = template, title = 'ACP')

    return fig


