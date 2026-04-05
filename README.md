# Real Estate Price AI Predictor - MLOps sur Snowflake

![Snowflake](https://img.shields.io/badge/Snowflake-29B5E8?style=flat&logo=snowflake&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![AWS S3](https://img.shields.io/badge/AWS_S3-232F3E?style=flat&logo=amazonaws&logoColor=white)

Pipeline de machine learning end-to-end pour la prédiction de prix immobiliers, construit intégralement dans Snowflake : de l'ingestion des données brutes jusqu'à une application d'inférence en temps réel.

---

## Sommaire

- [Présentation](#présentation)
- [Dataset](#dataset)
- [Architecture du Pipeline](#architecture-du-pipeline)
- [Analyse exploratoire](#analyse-exploratoire)
- [Feature Engineering](#feature-engineering)
- [Performances des modèles](#performances-des-modèles)
- [Modèle final — VotingRegressor](#modèle-final--votingregressor)
- [Inférence](#inférence)
- [Application Streamlit](#application-streamlit)
- [Structure du dépôt](#structure-du-dépôt)
- [Notes techniques](#notes-techniques)
- [Environnement](#environnement)

---

## Présentation

Ce projet a été développé dans le cadre de l'évaluation Data Engineering & MLOps du programme MBAESG. L'objectif était de construire un pipeline ML complet sur Snowflake sans déplacer les données vers un environnement externe, en s'appuyant sur Snowpark, les Snowflake Notebooks et le Snowflake Model Registry.

Le pipeline couvre l'ingestion des données depuis S3, la déduplication, le feature engineering, l'entraînement et la sélection de modèles, l'optimisation des hyperparamètres, l'enregistrement du modèle, l'inférence par lot, et une application Streamlit pour les prédictions en temps réel.

---

## Dataset

Le dataset décrit des propriétés résidentielles et leur prix de vente. Il provient d'un bucket S3 et a été chargé dans Snowflake via un stage externe au format JSON.

| Variable | Description |
|---|---|
| `PRICE` | Prix de vente de la propriété (cible) |
| `AREA` | Surface totale (m²) |
| `BEDROOMS` | Nombre de chambres |
| `BATHROOMS` | Nombre de salles de bain |
| `STORIES` | Nombre d'étages |
| `MAINROAD` | Accès à une route principale (yes/no) |
| `GUESTROOM` | Présence d'une chambre d'amis (yes/no) |
| `BASEMENT` | Présence d'un sous-sol (yes/no) |
| `HOTWATERHEATING` | Système de chauffage à eau chaude (yes/no) |
| `AIRCONDITIONING` | Climatisation (yes/no) |
| `PARKING` | Nombre de places de stationnement |
| `PREFAREA` | Situé dans une zone privilégiée (yes/no) |
| `FURNISHINGSTATUS` | furnished / semi-furnished / unfurnished |

Après déduplication, environ 50 % des lignes ont été supprimées en tant que doublons exacts.

---

## Architecture du Pipeline

```
Bucket S3  (format JSON)
    └── Stage externe Snowflake  (HOUSE_ASSETS)
            └── Table brute  (HOUSE_PRICE_RAW)
                    └── Déduplication  (modin → .to_pandas())
                            └── Feature Engineering  (6 variables construites)
                                    └── Pipeline sklearn
                                        ├── FunctionTransformer  (preprocessing)
                                        ├── FunctionTransformer  (feature_engineering)
                                        └── ColumnTransformer
                                            ├── RobustScaler   → AREA, AREA_PER_STORY, FURNISHED_AREA
                                            └── StandardScaler → autres features
                                                    └── Entraînement & sélection de modèles
                                                            └── Optimisation  (RandomizedSearchCV, n_jobs=1)
                                                                    └── Snowflake Model Registry
                                                                            └── Inférence SQL  (HOUSE_PRICE_PREDICTIONS)
                                                                                    └── Application Streamlit
```

---

## Analyse exploratoire

### Matrice de corrélation

<img width="1460" height="1051" alt="image" src="https://github.com/user-attachments/assets/76902226-c1e2-4262-a8f2-41bfe6bb746d" />

Les variables les plus corrélées avec `PRICE` sont `AREA`, `BATHROOMS`, `AIRCONDITIONING` et `PREFAREA`. `HOTWATERHEATING` présente une corrélation faible (9 %) mais a été conservée pour son potentiel en feature engineering.

---

## Feature Engineering

Six variables ont été construites à partir des colonnes d'origine pour enrichir la représentation du bien :

| Variable construite | Formule | Interprétation |
|---|---|---|
| `AREA_PER_STORY` | `AREA / STORIES` | Surface utile par étage |
| `BATH_BED_RATIO` | `BATHROOMS / BEDROOMS` | Ratio confort sanitaire |
| `COMFORT_SCORE` | `AIRCONDITIONING + HOTWATERHEATING + BASEMENT + GUESTROOM` | Score d'équipement |
| `LOCATION_SCORE` | `MAINROAD + PREFAREA` | Score de localisation |
| `HAS_PARKING` | `PARKING > 0` | Présence de stationnement |
| `FURNISHED_AREA` | `AREA × FURNISHINGSTATUS` | Surface pondérée par l'ameublement |

`AREA`, `AREA_PER_STORY` et `FURNISHED_AREA` sont mis à l'échelle avec un `RobustScaler` (résistant aux outliers détectés sur `AREA`). Les autres features reçoivent un `StandardScaler`.

---

## Performances des modèles

Validation croisée à 5 plis (`KFold(n_splits=5, shuffle=True, random_state=42)`), split train/test 80/20 fixe. Le jeu de test n'est utilisé qu'en évaluation finale.

Lors de l'analyse de la distribution des prix, les graphiques montrent la présence de beaucoup d'outliers. 

<img width="1460" height="515" alt="image" src="https://github.com/user-attachments/assets/872227d4-9601-452b-8b4e-899a78802d26" />

Un modèle BayesianRidge+log a donc été testé et la cible `PRICE` a été transformée via `log1p` / `expm1` (`TransformedTargetRegressor`) pour atténuer l'effet des outliers.

### Comparaison des modèles

| Modèle | R² CV | R² Test | Overfitting|
|---|---|---|---|
| BayesianRidge | 0.6832 | 0.6576 | 0.0256 |
| Ridge | 0.6857 | 0.6559 | 0.0298 |
| GradientBoostingRegressor | 0.8769 | 0.7019 | 0.1750 |
| RandomForestRegressor | 0.9434 | 0.6355 | 0.3079 |
| LinearRegression | 0.6858 | 0.6542 | 0.0316 |
| BayesianRidge+log | 0.6949 | 0.6289 | 0.0660 |

> Le RandomForest a été écarté pour son overfitting élevé. Sur ce dataset de taille réduite, les modèles linéaires généralisent mieux que les méthodes ensemblistes complexes.
> Le BayesianRidge+log n'apporte pas de performances supplémentaires par rapport à la version initiale.

### Feature Importance — BayesianRidge

<img width="1460" height="1016" alt="image" src="https://github.com/user-attachments/assets/5d5d9904-f126-4b41-97b2-224863d4ffb9" />

L'analyse des coefficients du BayesianRidge (après scaling) révèle les variables les plus déterminantes dans l'estimation du prix.

---

## Modèle final — VotingRegressor

Après comparaison du Stacking et du Voting sur les trois meilleurs candidats, le `VotingRegressor` a été retenu pour son meilleur compromis R²/overfitting.

| Composant | Rôle |
|---|---|
| `BayesianRidge` | Modèle le plus stable, faible overfitting |
| `Ridge` | Régularisation L2, bonne généralisation |
| `GradientBoostingRegressor` | Capture les non-linéarités |


| Métrique | Valeur |
|---|---|
| R² CV | 0.6585 |
| R² Test | 0.6885 |
| Overfitting | 0.0837 |
| MAE | 43.362 |
| RMSE | 62.584 |

Le modèle est enregistré dans le **Snowflake Model Registry** sous le nom `house_price_voting` (version `v1`) dans `HOUSE_PRICE_DB.HOUSE_SCHEMA`.

---

## Inférence

Les prédictions sont générées directement en SQL via `!PREDICT()` sur la table de test, et stockées dans `HOUSE_PRICE_PREDICTIONS` :

```sql
SELECT
    AREA, BEDROOMS, ...,
    HOUSE_PRICE_VOTING!PREDICT(
        AREA, BEDROOMS, BATHROOMS, STORIES,
        MAINROAD, GUESTROOM, BASEMENT, HOTWATERHEATING,
        AIRCONDITIONING, PARKING, PREFAREA, FURNISHINGSTATUS
    )['output_feature_0']::FLOAT AS PREDICTED_PRICE
FROM HOUSE_PRICE_DB.HOUSE_SCHEMA.HOUSE_PRICE_TEST_DATA;
```

---

## Application Streamlit

L'application propose une interface d'estimation en temps réel construite avec Streamlit-in-Snowflake.

### Renseignement des informations

<img width="1568" height="784" alt="image" src="https://github.com/user-attachments/assets/8354a766-1137-4852-87f0-ca67241dfe8f" />

Sur la partie gauche l'utilisateur peut modifier les informations du bien et la page d'accueil se met à jour automatiquement.

### Prédiction

<img width="1563" height="872" alt="image" src="https://github.com/user-attachments/assets/d1aa8284-4de0-4fc6-a348-7579ab88adc9" />

Une fois la prédiction réalisée, l'interface affiche un compte rendu global du bien et de ses caractéristiques. On y trouve aussi les informations du modèle utilisé.

### Fonctionnalités

- Sidebar avec contrôles pour les 13 variables du bien (sliders et menus déroulants)
- Jauge Plotly affichant le prix estimé
- Barres de score (confort, localisation, surface, pièces, finitions, parking)
- Chips d'équipements résumant le profil du bien
- Métrique prix au m² calculée à partir de la prédiction

### Déploiement

L'application est disponible dans `streamlit.py`. Pour la déployer dans Snowflake :

1. Dans Snowsight, aller dans **Streamlit** → **+ Streamlit App**
2. Copier-coller le contenu de `streamlit.py`
3. Ajouter le package `plotly` via le menu **Packages**
4. Sélectionner le warehouse et la base `HOUSE_PRICE_DB`
5. Lancer l'application

---

## Structure du dépôt

```
.
├── pipeline.ipynb        # Notebook Snowflake — pipeline ML complet
├── streamlit.py          # Application Streamlit-in-Snowflake
├── environment.yml       # Environnement Python Snowflake
└── README.md
```

---

## Notes techniques

- `n_jobs=1` requis pour `RandomizedSearchCV` dans les Snowflake Notebooks — le multiprocessing joblib n'est pas supporté dans le sandbox
- La frontière modin/Snowpark est établie une seule fois après déduplication via `.to_pandas()`, avant toutes les opérations sklearn
- Le Snowflake Model Registry requiert `sample_input_data=X_train` pour l'inférence de schéma à l'enregistrement
- L'inférence Streamlit utilise les valeurs littérales directement dans la requête SQL pour éviter les restrictions sur les tables/vues temporaires

---

## Environnement

```yaml
name: app_environment
channels:
  - snowflake
dependencies:
  - catboost=*
  - matplotlib=*
  - modin=*
  - plotly=*
  - py-xgboost=*
  - scikit-learn=*
  - seaborn=*
  - snowflake-ml-python=*
  - snowflake-snowpark-python=*
```
