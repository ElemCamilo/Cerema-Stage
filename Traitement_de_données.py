import pandas as pd
import numpy as np
import ast

def df_label(df): #libelé du panneau d'arret
    Icon1 = df['FT'] == 1 
    Icon2 = df['ST'] == 1 
    Icon3 = df['PP'] == 1

    Icon1 = Icon1.replace(True, "feu rouge")
    Icon2 = Icon2.replace(True, "panneau stop")
    Icon3 = Icon3.replace(True, "passage piéton")

    Icon1 = Icon1.replace(False, None)
    Icon2 = Icon2.replace(False, None)
    Icon3 = Icon3.replace(False, None)

    Icon = Icon1.fillna(Icon2)
    Icon = Icon.fillna(Icon3)

    df = df.assign(Label = Icon)
    return df

#Création du lien StreetView pour la map
def StreetView(df):
    df['Latitude'] = df['Latitude'].astype(str)
    df['Longitude'] = df['Longitude'].astype(str)
    df['StreetView'] = "https://www.coordonnees-gps.fr/street-view/@" + df['Latitude'] + "," + df['Longitude'] + ",h117,p41,z1"
    return df

def Icon(df): 
    #icon de voiture
    df = df.assign(Icon = "car-taxi") 

    #Création d'un icon pour les feux tricolores
    Icon1 = df['FT'] == 1
    # Création d'un icon pour les panneaux stops
    Icon2 = df['ST'] == 1
    #Création d'un icon pour les passages piétons 
    Icon3 = df['PP'] == 1

    Icon1 = Icon1.replace(False, None)
    Icon2 = Icon2.replace(False, None)
    Icon3 = Icon3.replace(False, None)
    Icon = Icon1.fillna(Icon2)
    Icon = Icon.fillna(Icon3)
    Icon = Icon.replace(True, "cancel")

    df = df.assign(Icon2 = Icon)

    return df

def label():
    label = {'Gear' : 'Rapport de boîte de vitesse',
    'Slope': 'pente',
    'CumFuel': 'Consommation cumulée de carburant',
    'SystemType': 'Type du sysème',
    'StreetView': 'lien StreetView',
    'DriverID': 'Conducteur',
    'Tripnumber': 'Trajet',
    'InstantSpeed_CAN': 'vitesse instantanée',
    'SpeedLimit': 'limite de la vitesse',
    'Distance_cum': 'Distance cumulée',
    'temps_min': 'temps (min)',
    'Timestamp': 'temps (timestamp)',
    'smoothed_Acceleration_MM': 'Acceleration lissée',
    'ConsoFuel': 'Conso instantanée',
    'DuréeTrajet': 'Durée du trajet',
    'NombreStops': 'Nombre de stops',
    'Allure': 'Allure du conducteur',

    }
    return label
    
#calculer la consommation de carburant en L/100
def calcul_conso(df):
    df2 = df['CumFuel'].shift(periods = 1)
    df2[0] = 0
    df = df.assign(CumFuelp = df2)
    Conso = df['CumFuel'] - df['CumFuelp']
    df = df.drop(columns = 'CumFuelp')
    df = df.assign(ConsoFuel = Conso)
    return(df)

#Agrégé par trajet
def calcul_distance(df):
    df2 = df['Distance_cum'].shift(periods = 1)
    df2[0] = 0
    df = df.assign(Distance_cump = df2)
    Distance = df['Distance_cum'] - df['Distance_cump']


    df = df.drop(columns = 'Distance_cump')
    df = df.assign(DistanceInstant = Distance)
    return(df)

# Calcul le temps d'arret, pas le nombre de stops ! -> creer df avec ligne précédente
def calcul_stops(df):
    #df2 représente le point précédent du dataframe
    df2 = df['InstantSpeed_CAN'].shift(periods = 1)
    df2[0] = 0
    df = df.assign(vitessep = df2)

    #calcul du nombre de stops
    liste = df['InstantSpeed_CAN'] == 0
    liste2 = df['vitessep'] !=0
    liste3 = liste * liste2
    liste3 = list(liste3)
    df = df.drop(columns = 'vitessep')

    df = df.assign(NombreStops = liste3)
    # df3 = pd.DataFrame()
    # df3 = df3.assign(NombreStops = liste3)
    # df3 = df['NombreStops'].replace(True, "nombre d'arrêt")
    # df = df.assign(NombreStops = df['NombreStops'])
    return(df)

def temps_min(df):
    #calcul de la durée des trajets
    Timestamp2 = df['Timestamp'].shift(periods = 1)
    Timestamp2[0] = 0
    df = df.assign(Timestamp2 = Timestamp2)

    Duree = df['Timestamp'] - df['Timestamp2']
    df = df.assign(temps_min = Duree.cumsum(skipna = True))

    #transformation du timestamp en datetime
    df['temps_min'] = pd.to_datetime(df['temps_min'] * 1000000)
    df['temps_min'] = df['temps_min'].dt.time
    df['temps_min'] = df['temps_min'].astype(str)
    df['temps_min'] = df['temps_min'].str[:8] #choix de prendre %H:%M:%S:

    df = df.drop(columns = ['Timestamp2'])
    return df

#Agrégé par trajet 
#Agrégé par trajet 
def calcul_temps(df):
    df3 = pd.DataFrame()
    Duree = []
    for i in df['Tripnumber'].unique():
        df2 = df[df['Tripnumber'] == i]
        df2 = df2.reset_index()
        Duree.append((df2['Timestamp'][len(df2)-1] - df2['Timestamp'][0]))

    df3 = df3.assign(temps = Duree)
    df3['temps'] = pd.to_datetime(df3['temps']*1000000)
    df3['temps'] = df3['temps'].dt.minute
    return list(df3['temps'])



def temps_arrêt_camembert(df):
    #creéation de 3 liste pour les cas suivants:
    liste1 = df['InstantSpeed_CAN'] == 0 #arret
    liste2 = df['InstantSpeed_CAN'] > df['SpeedLimit'] #depassement
    liste3 = df['InstantSpeed_CAN'] != 0# pas d'arret
    liste4 = df['InstantSpeed_CAN'] <= df['SpeedLimit'] #pas de dépassement
    liste5 = liste3 & liste4

    #concaténation des 3 lignes en une seule pour le plot
    liste1 = liste1.replace(True,'arret')
    liste1 = liste1.replace(False, None)
    liste2 = liste2.replace(True, 'depassement')
    liste2 = liste2.replace(False,None)
    liste5 = liste5.replace(True,'pas de depassement')
    liste5 = liste5.replace(False,None)
    liste = liste1.fillna(value = liste2)
    liste = liste.fillna(value = liste5)

    return liste

def temps_arrêt_barre(df):
    n = len(df['Tripnumber'].unique())
    Arret = np.zeros(n)
    Depassement = np.zeros(n)
    Respect = np.zeros(n)

    k=0
    #Pour chaque trajet
    for i in df['Tripnumber'].unique():

        df2 = df[df['Tripnumber'] ==i]
        df2 = df2.reset_index()
        liste1 = list(df2['InstantSpeed_CAN'] == 0) #arret
        liste2 = list(df2['InstantSpeed_CAN'] > df2['SpeedLimit']) #depassement
        liste3 = df2['InstantSpeed_CAN'] != 0# pas d'arret
        liste4 = df2['InstantSpeed_CAN'] <= df2['SpeedLimit'] #pas de dépassement

        liste5 = list(liste3 * liste4)

        Arret[k] = liste1.count(True)/len(df2) * 100
        Depassement[k] = liste2.count(True)/len(df2) * 100
        Respect[k] = liste5.count(True)/len(df2) * 100

        k+=1
    return(Respect,Arret,Depassement)


def to_dictionnaire_et_liste(df):
    df['Dictionnaire'][0] = ast.literal_eval(df['Dictionnaire'][0])
    df['Dictionnaire'][1] = df['Dictionnaire'][1][1:-1].split(',')
    df['Dictionnaire'][2] = ast.literal_eval(df['Dictionnaire'][2])