# Making Change — Python → Excel

Générateur local de rapports Excel sur le risque de change d'une dette en EUR et de flux disponibles en XAF. Aucun serveur web, aucune API de marché.

## Installation et génération

Python 3.11 ou supérieur :

```bash
python -m venv .venv
# Linux / macOS
source .venv/bin/activate
# Windows : .venv\Scripts\activate
python -m pip install -r requirements.txt
python generate_excel.py
```

Le résultat est `outputs/making_change.xlsx` (non versionné). Le classeur contient : synthèse et trois graphiques, hypothèses, échéancier annuel, quatre scénarios comparés, sensibilité, méthode et références.

Pour modifier les hypothèses :

```bash
python generate_excel.py --inputs example_inputs.json --output outputs/mon_cas.xlsx
```

Les taux et parts sont des fractions (0.20 = 20 %). Le taux de change est exprimé en XAF pour un EUR. Le JSON doit contenir tous les paramètres indiqués dans l'exemple. Les valeurs doivent être finies ; durée entière de 1 à 30 ans, principal et taux de change strictement positifs, dépréciation entre 0 inclus et 1 exclu. Intérêt, frais et couverture sont bornés entre 0 et 1 ; CFADS positif ou nul.

**Le classeur est un instantané calculé par Python**, pas un modèle Excel recalculable : modifier une cellule d'hypothèse ne modifie pas les résultats. Modifier le JSON et relancer le script. Les graphiques reprennent les valeurs exportées. Aucun arrondi intermédiaire dans les calculs ; arrondi d'affichage uniquement.

## Méthode et prudence scientifique

- Cas classique construit : SPV fictive d'infrastructure, pas une entreprise réelle ni un cas académique reproduit.
- Principal amorti à parts annuelles égales, intérêts sur l'encours initial, CFADS constant.
- Dépréciation `d` : taux stressé `S / (1-d)`, atteint immédiatement et maintenu pendant toute la durée.
- Couverture : fraction constante de chaque service annuel convertie au taux couvert fourni ; frais sur cette fraction convertie. Les frais sont inclus dans le service couvert pour calculer le DSCR.
- DSCR = CFADS / service annuel en monnaie locale. Les totaux sont nominaux, non actualisés. Les économies de couverture sont nettes des frais et peuvent être négatives.
- XAF/EUR est une parité fixe : le stress est une rupture hypothétique de parité, sans probabilité attribuée.
- Le taux couvert par défaut égale le spot initial à toutes les maturités : ce n'est pas un prix de forward ni une garantie de disponibilité de couverture. Pas de taux de marché, fiscalité, réserves, inflation, collatéral ou risque de contrepartie.
- Les références du classeur encadrent la question de recherche ; elles ne valident ni ce calibrage ni un effet causal de la couverture. Les textes intégraux n'ont pas été revérifiés pour cette version.

## Tests

```bash
python -m unittest discover -s tests -v
```

Les tests couvrent les calculs, les entrées invalides, la parité entre le moteur et le fichier Excel relu, les scénarios et la présence des graphiques.

## Structure

```text
model.py               Moteur déterministe, sans dépendance externe
generate_excel.py      Générateur de classeur (openpyxl)
example_inputs.json    Paramètres reproductibles
tests/                Tests unitaires
these/                 Travaux et bibliographie de recherche conservés
data/                 Données et protocole d'anonymisation conservés
```

Les anciennes interfaces web et configurations de déploiement ont été retirées. Le retrait du code ne désactive pas automatiquement un ancien hébergement : désactiver la publication dans les paramètres GitHub Pages du dépôt si nécessaire. L'historique Git n'est pas réécrit.

Prototype exploratoire dans un cadre de recherche SKEMA Business School (référence institutionnelle uniquement). Aucun conseil financier. Ne publier aucune donnée personnelle, confidentielle ou bancaire non anonymisée.
