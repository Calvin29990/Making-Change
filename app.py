"""Making Change — research prototype, not financial advice."""
import io
import csv
from dataclasses import replace
import streamlit as st
from model import Inputs, simulate

st.set_page_config(page_title='Making Change', layout='wide')
st.title('Making Change')
st.caption('Prototype de recherche | Risque de change, dette et infrastructure')
st.warning("Simulation illustrative, pas une prévision, une recommandation financière ou une cotation. Saisies locales, sans données de marché ni exécution bancaire.")

with st.sidebar:
    st.header('Profil entreprise')
    name = st.text_input('Entreprise ou projet', 'Projet exemple')
    size = st.selectbox('Taille', ['TPE', 'PME', 'ETI', 'Grande entreprise', 'Projet / autre'])
    region = st.text_input('Pays ou géographie', 'Gabon')
    sector = st.text_input('Secteur', 'Infrastructure')
    local = st.text_input('Devise de revenus (code)', 'XAF').upper().strip()
    foreign = st.text_input('Devise de dette (code)', 'EUR').upper().strip()
    st.caption('Profil descriptif uniquement : il ne modifie pas les calculs.')

st.subheader('1. Hypothèses du projet')
a, b, c = st.columns(3)
principal = a.number_input('Dette initiale en devise étrangère', min_value=0.01, value=10000000.0, step=100000.0)
years = b.slider('Durée de remboursement (années)', 1, 30, 15)
interest = c.number_input('Taux annuel de la dette (%)', min_value=0.0, max_value=100.0, value=5.0, step=0.5)
a, b, c = st.columns(3)
rate = a.number_input('Taux initial : unités locales / 1 unité de dette', min_value=0.000001, value=655.957, format='%.6f')
cfads = b.number_input('CFADS annuel en monnaie locale', min_value=0.0, value=850000000.0, step=10000000.0, help='Flux de trésorerie disponible pour le service de la dette, avant principal et intérêts.')
threshold = c.number_input('Seuil DSCR indicatif (saisi par vous)', min_value=0.0, value=1.20, step=0.05)
if {local, foreign} == {'XAF', 'EUR'}:
    st.info('XAF/EUR : le taux saisi est une hypothèse. Un choc sur cette paire doit être interprété comme une rupture hypothétique de parité, pas une variation ordinaire. La vérification du régime et de sa date est à effectuer séparément.')
if local == foreign:
    st.warning('Même devise sélectionnée : le choc de change doit normalement être nul.')

st.subheader('2. Scénarios et couverture illustrative')
a, b, c = st.columns(3)
shock = a.slider('Dépréciation de la monnaie locale (%)', 0, 80, 20, 5)
cover = b.selectbox('Part du service de la dette couverte (%)', [0, 25, 50, 100], index=2)
fwd = c.number_input('Taux couvert supposé : local / devise', min_value=0.000001, value=rate, format='%.6f', help='Saisi par vous : ce n’est pas une cotation forward.')
cost = st.number_input('Coût hypothétique par an (% du service couvert)', min_value=0.0, max_value=100.0, value=0.0, step=0.1)
x = Inputs(principal, interest / 100, years, rate, cfads, shock / 100, cover / 100, fwd, cost / 100)
rows = simulate(x)
first = rows[0]
st.subheader(f'3. Résultats — {name}')
a, b, c, d = st.columns(4)
a.metric('Taux du scénario', f"{first['Taux scénario']:,.2f} {local}/{foreign}")
b.metric('Service année 1 sans couverture', f"{first['Service sans couverture (local)']:,.0f} {local}")
c.metric('Service année 1 avec couverture', f"{first['Service avec couverture (local)']:,.0f} {local}")
d.metric('DSCR année 1 avec couverture', f"{first['DSCR avec couverture']:.2f}x")
minimum = min(r['DSCR avec couverture'] for r in rows)
st.write(f'DSCR minimal sur la période : **{minimum:.2f}x** — seuil indicatif saisi : **{threshold:.2f}x**. ' + ('Sous le seuil au moins une année.' if minimum < threshold else 'Au-dessus ou égal au seuil dans ce modèle.'))
st.dataframe(rows, hide_index=True, width='stretch')
st.subheader('Comparer les scénarios et les couvertures')
comparison = []
for s in [0, 5, 10, 20]:
    for h in [0, 25, 50, 100]:
        result = simulate(replace(x, depreciation=s/100, coverage=h/100))
        comparison.append({'Dépréciation (%)': s, 'Couverture (%)': h,
                           'Taux scénario': result[0]['Taux scénario'],
                           'Service année 1 local': result[0]['Service avec couverture (local)'],
                           'DSCR année 1': result[0]['DSCR avec couverture'],
                           'DSCR minimum': min(r['DSCR avec couverture'] for r in result)})
st.dataframe(comparison, hide_index=True, width='stretch')
buf = io.StringIO(newline='')
writer = csv.DictWriter(buf, fieldnames=list(rows[0]))
writer.writeheader(); writer.writerows(rows)
st.download_button('Télécharger le détail annuel (CSV)', buf.getvalue().encode('utf-8-sig'), 'simulation.csv', 'text/csv')
st.markdown('''### Lecture et limites
- L’outil compare des **charges de dette**, pas la valeur de l’entreprise ni une exposition économique complète. Les revenus et le CFADS sont supposés constants en monnaie locale.
- Principal remboursé en parts annuelles égales ; intérêts sur le capital restant en début d’année. Choc immédiat puis constant ; pas d’inflation, fiscalité, refinancement ni défaut.
- La couverture est un **verrouillage hypothétique** d’une part de chaque échéance, au taux saisi, avec un coût simplifié. Aucun produit réel, disponibilité, marge bancaire ou risque de contrepartie n’est évalué. Un taux unique sur 15 ans n’est pas une cotation ni une garantie de disponibilité.
- Le seuil DSCR est indicatif : un ratio inférieur n’établit pas à lui seul une insolvabilité. Un gain relatif dans un scénario est une **opportunité à étudier**, pas une recommandation.

Fondements et limites : voir `docs/SOURCES-ACADEMIQUES.md` et `docs/METHODOLOGIE.md` dans le projet.
''')
