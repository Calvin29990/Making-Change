"""Generate an auditable, offline Excel report using the shared Python engine."""
import argparse
import json
from dataclasses import asdict, replace
from pathlib import Path

from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from model import Inputs, simulate

DEFAULT = Inputs(10_000_000, .05, 15, 655.957, 850_000_000, .20, .50, 655.957, 0)


def totals(rows):
    """Nominal totals; DSCR is the minimum annual ratio, not an average."""
    return [sum(r['Service sans couverture (local)'] for r in rows),
            sum(r['Service avec couverture (local)'] for r in rows),
            sum(r['Coût couverture (local)'] for r in rows),
            min(r['DSCR sans couverture'] for r in rows),
            min(r['DSCR avec couverture'] for r in rows)]


def build_workbook(x: Inputs) -> Workbook:
    rows = simulate(x)  # Validate before creating any output file.
    wb = Workbook()
    summary = wb.active
    summary.title = 'Synthèse'
    summary.append(['Making Change — stress test de change', 'Valeur'])
    summary.append(['Cas', 'SPV fictive d’infrastructure ; aucune entreprise réelle'])
    summary.append(['Lecture', 'Instantané calculé par Python. Modifier le JSON et régénérer ; pas de recalcul Excel.'])
    summary.append(['Monnaies', 'EUR (dette), XAF (locale) ; taux en XAF par EUR'])
    summary.append(['Statut', 'Simulation pédagogique déterministe, pas une prévision ni un conseil.'])
    labels = ['Service sans couverture (XAF)', 'Service avec couverture (XAF)',
              'Frais de couverture (XAF)', 'DSCR minimum sans couverture', 'DSCR minimum avec couverture']
    for label, value in zip(labels, totals(rows)):
        summary.append([label, value])
    summary.append(['Économie nette de couverture (XAF)', totals(rows)[0] - totals(rows)[1]])
    summary.append(['Unités', 'Totaux nominaux sur la durée ; non actualisés. Une économie négative est un surcoût.'])

    assumptions = wb.create_sheet('Hypothèses')
    assumptions.append(['Paramètre Python / JSON', 'Valeur', 'Définition et provenance'])
    notes = [
        'Principal initial en EUR ; choix illustratif',
        'Taux annuel fixe sur le capital en début d’année ; choix illustratif',
        'Durée entière ; principal remboursé en fractions annuelles égales',
        'XAF/EUR initial ; convention de parité 655,957 dans le cas par défaut',
        'CFADS en XAF/an, constant ; choix illustratif, pas le chiffre d’affaires',
        'Perte de valeur du XAF ; choc immédiat et permanent, sans probabilité',
        'Part de chaque paiement annuel couverte ; hypothèse constante',
        'Taux couvert XAF/EUR ; hypothèse, pas une cotation de marché',
        'Frais en fraction du service annuel couvert converti au taux couvert',
    ]
    for (key, value), note in zip(asdict(x).items(), notes):
        assumptions.append([key, value, note])

    schedule = wb.create_sheet('Échéancier')
    schedule.append(list(rows[0]))
    for row in rows:
        schedule.append(list(row.values()))

    scenarios = wb.create_sheet('Scénarios')
    scenarios.append(['Scénario'] + labels)
    for label, params in [('Sans choc, couverture choisie', replace(x, depreciation=0)),
                          ('Choc choisi, sans couverture', replace(x, coverage=0)),
                          ('Choc et couverture choisis', x),
                          ('Choc choisi, couverture totale', replace(x, coverage=1))]:
        scenarios.append([label] + totals(simulate(params)))

    sensitivity = wb.create_sheet('Sensibilité')
    sensitivity.append(['Dépréciation XAF', 'DSCR minimum sans couverture', 'DSCR minimum avec couverture'])
    for shock in sorted(set([k / 100 for k in range(0, 81, 5)] + [x.depreciation])):
        values = totals(simulate(replace(x, depreciation=shock)))
        sensitivity.append([shock] + values[3:])

    method = wb.create_sheet('Méthode et limites')
    method.append(['Élément', 'Définition'])
    for row in [
        ('Taux stressé', 'S / (1 − d). Une perte de valeur de 20 % du XAF augmente XAF/EUR de 25 %.'),
        ('Principal annuel', 'P / N ; capital initial de l’année t = P − (t−1) × P/N.'),
        ('Service EUR', 'P/N + capital initial de l’année × taux d’intérêt annuel.'),
        ('Service non couvert', 'Service EUR × taux stressé.'),
        ('Frais', 'Service EUR × part couverte × taux couvert × taux de frais.'),
        ('Service couvert', 'Service EUR × [(1−part couverte) × taux stressé + part couverte × taux couvert] + frais.'),
        ('DSCR', 'CFADS / service en XAF ; frais inclus dans le dénominateur du scénario couvert.'),
        ('Interprétation', 'DSCR < 1 : CFADS insuffisant pour rembourser. Aucun covenant réel ni défaut juridique modélisé.'),
        ('Régime de change', 'XAF/EUR est une parité fixe : le choc représente une rupture hypothétique, pas une fluctuation ordinaire.'),
        ('Couverture', 'Le taux couvert par défaut égale le spot initial pour toutes les échéances : pas de valorisation de forward.'),
        ('Exclusions', 'Pas de courbe de taux, liquidité, collatéral, contrepartie, fiscalité, réserves, inflation ou réaction du CFADS.'),
        ('Portée', 'Les paramètres ne proviennent pas d’un cas académique publié. Aucune validation empirique ni causalité démontrée.'),
        ('Reproductibilité', 'Valeurs calculées par model.py, sans formules Excel, macros ni connexion externe. Les graphiques utilisent ces valeurs.'),
        ('Sources', 'Références issues du registre du projet ; textes intégraux non revérifiés lors de cette génération.'),
    ]:
        method.append(row)

    sources = wb.create_sheet('Références')
    sources.append(['Référence', 'DOI', 'Apport et limite'])
    for row in [
        ('Adler & Dumas (1984), Exposure to Currency Risk: Definition and Measurement', 'https://doi.org/10.2307/3665446', 'Exposition économique, plus large que le service contractuel isolé ici.'),
        ('Froot, Scharfstein & Stein (1993), Risk Management: Coordinating Corporate Investment and Financing Policies', 'https://doi.org/10.1111/j.1540-6261.1993.tb05123.x', 'Frictions de financement ; ne calibre pas ce prêt ni le prix de couverture.'),
        ('Kleimeier & Megginson (2000), Are Project Finance Loans Different from Other Syndicated Credits?', 'https://doi.org/10.1111/j.1745-6622.2000.tb00043.x', 'Cadre du financement de projet ; pas une validation du modèle simplifié.'),
        ('Allayannis & Weston (2001), The Use of Foreign Currency Derivatives and Firm Market Value', 'https://doi.org/10.1093/rfs/14.1.243', 'Association empirique sur grandes entreprises américaines, pas preuve causale applicable à cette SPV.'),
    ]:
        sources.append(row)

    def chart(kind, title, sheet, columns, anchor):
        c = kind()
        c.title = title
        c.y_axis.title = 'DSCR (x)' if kind is LineChart else 'XAF'
        c.x_axis.title = 'Dépréciation' if sheet is sensitivity else 'Année'
        for col in columns:
            c.add_data(Reference(sheet, min_col=col, min_row=1, max_row=sheet.max_row), titles_from_data=True)
        c.set_categories(Reference(sheet, min_col=1, min_row=2, max_row=sheet.max_row))
        c.width, c.height = 22, 11
        summary.add_chart(c, anchor)

    chart(LineChart, 'DSCR annuel', schedule, [11, 12], 'D2')
    chart(BarChart, 'Service annuel en XAF', schedule, [7, 8], 'D24')
    chart(LineChart, 'Sensibilité au choc de change', sensitivity, [2, 3], 'D46')

    for ws in wb:
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions
        ws.sheet_view.showGridLines = False
        for cell in ws[1]:
            cell.fill = PatternFill('solid', fgColor='193C50')
            cell.font = Font(color='FFFFFF', bold=True)
        for row in ws.iter_rows(min_row=2):
            for cell in row:
                cell.alignment = Alignment(vertical='top', wrap_text=True)
                if isinstance(cell.value, float):
                    cell.number_format = '#,##0.00;[Red]-#,##0.00'
        for col in range(1, ws.max_column + 1):
            ws.column_dimensions[get_column_letter(col)].width = 26 if ws is schedule else 45
    for n in range(2, sensitivity.max_row + 1):
        sensitivity.cell(n, 1).number_format = '0%'
    return wb


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, help='JSON contenant tous les champs de Inputs (voir example_inputs.json)')
    parser.add_argument('--output', type=Path, default=Path('outputs/making_change.xlsx'))
    args = parser.parse_args(argv)
    try:
        x = Inputs(**json.loads(args.inputs.read_text(encoding='utf-8'))) if args.inputs else DEFAULT
        wb = build_workbook(x)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        wb.save(args.output)
    except (ValueError, TypeError, OSError) as exc:
        parser.error(str(exc))
    print(f'Classeur généré : {args.output}')


if __name__ == '__main__':
    main()
