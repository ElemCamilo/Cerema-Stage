import pandas as pd
import numpy as np
import ast

def max_trip(df):
    df2 = df.groupby(["DriverID"]).last().reset_index()                                  # On fait un group by par DriverID et on garde le dernier DriverID de chaque groupe
    df3 = df2[df2['Tripnumber'] == np.max(df2['Tripnumber'])]                            # On restreint le dataframe au Tripnumber le plus grand        
    df3 = df3.reset_index()                                                              # Comme on a fait un groupby par DriverID, on fait ça pour avoir à nouveau DriverID sous la forme d'une colonne utilisable dans le dataframe 
    return df3['DriverID'][0]                                                            # On retourne le/un des DriverID qui a le numéro de trajet le plus grand

def colonnes(df,df_config):
    for i in df_config['Dictionnaire'][0]:                                               # On parcourt le dictionnaire 
        if df_config['Dictionnaire'][0][i] == 'nan':                                     # Si la valeur de la clé est nan
            df[i] = np.nan                                                               # On definit la ième colonne comme un nan
            df_config['Dictionnaire'][0][i] = i                                          # Par la suite pour pouvoir y accéder au dictionnaire on a besoin que la valeur ne soit pas nan
    return(df,df_config)                                                                

def variables(df_config):                                                                # On definit le variables générales associés au nom des colonnes 
    vitesse = df_config['Dictionnaire'][0]['vitesse instantanee']
    temps = df_config['Dictionnaire'][0]['Timestamp']
    limite = df_config['Dictionnaire'][0]['limite de la vitesse']
    Conducteur =  df_config['Dictionnaire'][0]['Conducteur']
    Trajet =  df_config['Dictionnaire'][0]['Trajet']
    Longitude = df_config['Dictionnaire'][0]['Longitude']                 
    Latitude = df_config['Dictionnaire'][0]['Latitude']
    pente = df_config['Dictionnaire'][0]['pente']
    conso = df_config['Dictionnaire'][0]['Consommation de carburant']
    gear = df_config['Dictionnaire'][0]['vitesse de boîte']
    DistanceCum = df_config['Dictionnaire'][0]['Distance cumulée']
    Acceleration = df_config['Dictionnaire'][0]['Acceleration']
    smoothed_acceleration = df_config['Dictionnaire'][0]['Acceleration lissée']
    temps_min2 = df_config['Dictionnaire'][0]['temps (min)']
    SystemType = df_config['Dictionnaire'][0]['type du système']

    return vitesse, temps, limite, Conducteur, Trajet, Longitude, Latitude, pente, conso, gear, DistanceCum, Acceleration, smoothed_acceleration, temps_min2, SystemType


def df_label(df):                                                                        # Ici on définit le label qui apparait qu'on on met le curseur sur la map
    Icon1 = df['FT'] == 1 
    Icon2 = df['ST'] == 1                                                                # Listes de True et de False indiquant si les lignes des colonnes associés(FT, ST, PP) valent 1 ou pas 
    Icon3 = df['PP'] == 1

    Icon1 = Icon1.replace(True, "feu rouge")
    Icon2 = Icon2.replace(True, "panneau stop")                                          # On remplace la valeur True par une chaine de caractères correspondante
    Icon3 = Icon3.replace(True, "passage piéton")

    Icon1 = Icon1.replace(False, None)
    Icon2 = Icon2.replace(False, None)
    Icon3 = Icon3.replace(False, None)

    Icon = Icon1.fillna(Icon2)                                                           # On croise Icon1 et Icon2, comme on ne peut pas avoir un panneau stop et un feu rouge au même temps, on remplit les espaces vides de Icon1
    Icon = Icon.fillna(Icon3)                                                            # Liste définitive des icônes

    df = df.assign(Label = Icon)                                                         # On définit la nouvelle colonne Label par la liste Icon
    return df


def StreetView(df):                                                                      # Création du lien StreetView pour la map
    df2 = df[['Latitude','Longitude']]
    df2['Latitude'] = df2['Latitude'].astype(str)                                        # On change le type des valeurs de la colonne
    df2['Longitude'] = df2['Longitude'].astype(str)
    df['StreetView'] = "https://www.coordonnees-gps.fr/street-view/@" + df2['Latitude'] + "," + df2['Longitude'] + ",h117,p41,z1"  # Vectoriellement on définit les pages web associées à chaque latitue et longitude
    return df

def Icon(df):                                                                            # Crée la colonne qui va dire où est-ce qu'il y a un icône et où est-ce qu'il en a pas
                                                                                            
    df = df.assign(Icon = "car-taxi")                                                    # Icône de voiture
                                                                                         # Même principe que df_label, sauf qu'ici on definit l'icone 'cancel' qui vient inclut dans Kepler.gl, pour pouvoir repérer les feux rouges, les panneaux stop et les passages piéton avec un même icône

    Icon1 = df['FT'] == 1                                                                # Création d'un icône pour les feux tricolores
    Icon2 = df['ST'] == 1                                                                # Création d'un icône pour les panneaux stops                                     
    Icon3 = df['PP'] == 1                                                                # Création d'un icône pour les passages piétons  

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
    'InstantSpeed_CAN': 'vitesse instantanée',                                           # On définit les labels associés aux noms des colonnes
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
    
                                                                
def calcul_conso(df):                                                                    # Calculer la consommation instantanée de carburant par L/100
    CumFuelp = df['CumFuel'].shift(periods = 1)                                          # On crée une copie de la colonne CumFuel décalé de 1 indice 
    CumFuelp[0] = 0                                                                      

    df = df.assign(CumFuelp = CumFuelp)                                                  # On définit la colonne du dataframe CumFuelp par la liste créé
    Conso = df['CumFuel'] - df['CumFuelp']                                               # On crée la liste Conso vectoriellement pour plus d'efficacité en termes de temps de calcul. En effet après avoir fait cette soustraction là, ce qu'on fait c'est qu'on prend la valeur qui va juste après une autre, on soustrait les deux et on obtient la consomation instantanée

    df = df.assign(ConsoFuel = Conso)
        
    df['ConsoFuel'][df['ConsoFuel'] < 0] = 0                                             # On set toutes valeur des la colonne ConsoFuel à 0 si la valeur de base est négative
    return(df)


def calcul_distance(df):                                                                 
    df2 = df['Distance_cum'].shift(periods = 1)
    df2[0] = 0
    df = df.assign(Distance_cump = df2)                                                  # Même processus que pour calcul_conso mais dans ce cas là pour avoir la distance instantanée
    Distance = df['Distance_cum'] - df['Distance_cump']

    df = df.drop(columns = 'Distance_cump')
    df = df.assign(DistanceInstant = Distance)
    return(df)


def calcul_stops(df):                                                                    # Permet de compter le nombre de stops effectués dans un trajet (quand la vitesse au point i est égale à 0 mais la vitesse au point i-1 est différente de 0)                                        # Calcul du temps d'arret, pas le nombre de stops
    df2 = df['InstantSpeed_CAN'].shift(periods = 1)                                       
    df2[0] = 0
    df = df.assign(vitessep = df2)

    liste = df['InstantSpeed_CAN'] == 0                                                  # On crée une liste de booléens où InstantSpeed_CAN vaut 0
    liste2 = df['vitessep'] !=0                                                          # On crée une liste de booléens où vitessep est différent de 0
    liste3 = liste * liste2                                                              # On fait un peu de logique(opérateur 'et') pour avoir une nouvelle liste avec les deux informations  
    liste3 = list(liste3)
    df = df.drop(columns = 'vitessep')

    df = df.assign(NombreStops = liste3)
    return(df)

def heure(df):                                                                           # On crée une colonne qui donne l'heure
    df['heure'] = ''
    df['heure'] = pd.to_datetime(df['Timestamp']*1000000).dt.hour                        # to_datetime est une fonction python qui permet d'avoir la date et l'heure à partir du timestamp. On multiplie le timestamp par un facteur pour avoir la bonne date car c'est en milisecondes
    return df

def temps_min(df):                                                                       # Transforme le timestamp au format H%M%S%MS (revient à 0 pour chaque trajet)
    df2 = df[['DriverID', 'Tripnumber', 'Timestamp']]                                    # On prend les trois colonnes qui nous intéressent pour faire le traitement
    
    debut = df2.groupby(["DriverID", "Tripnumber"]).first()                              # On regroupe par DriverID et par Tripnumber et on prend le premier timestamp pour un driver et un trajet à chaque fois


    df3 = pd.DataFrame()
    df3 = df3.assign(debut = debut)                                                      
    df3 = df3.reset_index() 
    df = df.merge(df3)                                                                   # On ajoute la colonne debut au df de départ

    df = df.assign(temps_min = df['Timestamp'] - df['debut'])                            # On crée la colonne temps_min qui est le temps écoulé depuis le début du trajet du conducteur respectif
    df['temps_min'] = pd.to_datetime(df['temps_min']*1000000).dt.time                    # On tranforme le timestamp obtenu au format H%M%S%MS
    df['temps_min'] = df['temps_min'].astype(str)

    df = df.drop(columns = ['debut'])
    return df

#Agrégé par trajet 
def calcul_temps(df):                                                                    # calcul la durée d’un trajet grâce à un groupby (on prend le dernier timestamp et on le transforme en au format H%M%S%MS) permet un affichage différent de temps_min dans certains cas
    df2 = df[['DriverID', 'Tripnumber', 'Timestamp']]  
    
    Duree = df2.groupby(["DriverID", "Tripnumber"]).last() - df2.groupby(["DriverID", "Tripnumber"]).first()     # Dernier du trajet moins premier timestamp du trajet


    df3 = pd.DataFrame()
    df3 = df3.assign(DuréeTrajet = Duree)

    df3['DuréeTrajet'] = pd.to_datetime(df3['DuréeTrajet']*1000000)                      # Transforamtion du timestamp en datetime
    df3['DuréeTrajet'] = df3['DuréeTrajet'].dt.minute                                    # On prend juste les minutes

    df3 = df3.reset_index() 
    df = df.merge(df3)                                                                   # Jointure sur le dataframe entier
     
    return df



def temps_arrêt_camembert(df):                                                           # Calcul du temps d'arrêt pour le camembert
                                                                                         # Création de 3 liste pour les cas suivants:
    liste1 = df['InstantSpeed_CAN'] == 0                                                 # Arret       
    liste2 = df['InstantSpeed_CAN'] > df['SpeedLimit']                                   # Depassement
    liste3 = df['InstantSpeed_CAN'] != 0                                                 # Pas d'arret
    liste4 = df['InstantSpeed_CAN'] <= df['SpeedLimit']                                  # Pas de dépassement
    liste5 = liste3 & liste4
                                                                                         # Concaténation des 3 lignes en une seule pour le plot
    liste1 = liste1.replace(True,'arret')
    liste1 = liste1.replace(False, None)
    liste2 = liste2.replace(True, 'depassement')
    liste2 = liste2.replace(False,None)
    liste5 = liste5.replace(True,'pas de depassement')
    liste5 = liste5.replace(False,None)
    liste = liste1.fillna(value = liste2)
    liste = liste.fillna(value = liste5)

    return liste

def temps_arrêt_barre(df):                                                               # Calcul du temps à l'arrêt pour le diagramme en barres
    n = len(df['Tripnumber'].unique())
    Arret = np.zeros(n)                                                                  # Liste de zéros de taille n
    Depassement = np.zeros(n)
    Respect = np.zeros(n)

    k=0

    for i in df['Tripnumber'].unique():                                                  # Pour chaque trajet

        df2 = df[df['Tripnumber'] ==i]                                                   # On restreint le dataframe au Tripnumber i
        df2 = df2.reset_index()
        liste1 = list(df2['InstantSpeed_CAN'] == 0)                                      # Arret
        liste2 = list(df2['InstantSpeed_CAN'] > df2['SpeedLimit'])                       # Depassement
        liste3 = df2['InstantSpeed_CAN'] != 0                                            # Pas d'arret
        liste4 = df2['InstantSpeed_CAN'] <= df2['SpeedLimit']                            # Pas de dépassement

        liste5 = list(liste3 * liste4)

        Arret[k] = liste1.count(True)/len(df2) * 100                                     # Pourcentage du nombre d'occurences
        Depassement[k] = liste2.count(True)/len(df2) * 100
        Respect[k] = liste5.count(True)/len(df2) * 100

        k+=1
    return(Respect,Arret,Depassement)


def to_dictionnaire_et_liste(df):                                                        # Transforme les chaines de caractères en dictionnaire ou liste  
    df['Dictionnaire'][0] = ast.literal_eval(df['Dictionnaire'][0])                      # ast.literal_eval transforme la chaine de caractères en dictionnaire
    df['Dictionnaire'][1] = df['Dictionnaire'][1][1:-1].split(',')                       # On transforme la chaine de caractères en liste. On lui dit que le symbole qui sépare un élément d'un autre est ','
    df['Dictionnaire'][2] = ast.literal_eval(df['Dictionnaire'][2])