import json
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path

from openpyxl import load_workbook

from generate_excel import DEFAULT, build_workbook, main, totals
from model import simulate


class ExcelTests(unittest.TestCase):
    def test_round_trip_and_engine_parity(self):
        for x in (DEFAULT, replace(DEFAULT, years=1, coverage=1, depreciation=0, annual_cost_rate=.02)):
            with self.subTest(x=x), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'report.xlsx'
                build_workbook(x).save(path)
                wb = load_workbook(path, data_only=True)
                self.assertEqual(len(wb['Synthèse']._charts), 3)
                exported = list(wb['Échéancier'].values)
                expected = simulate(x)
                self.assertEqual(list(exported[0]), list(expected[0]))
                self.assertEqual(len(exported), x.years + 1)
                for row, exp in zip(exported[1:], expected):
                    for value, target in zip(row, exp.values()):
                        self.assertAlmostEqual(value, target, delta=max(1, abs(target)) * 1e-12)
                for n, value in enumerate(totals(expected), 6):
                    self.assertAlmostEqual(wb['Synthèse'].cell(n, 2).value, value, delta=max(1, abs(value))*1e-12)
                wb.close()

    def test_scenarios_and_sensitivity(self):
        wb = build_workbook(DEFAULT)
        rows = list(wb['Scénarios'].values)
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[2][1], rows[2][2])  # no hedge means equal services
        self.assertAlmostEqual(rows[4][2], rows[1][2])  # free full hedge at initial spot
        sensitivity = list(wb['Sensibilité'].values)[1:]
        self.assertEqual(len(sensitivity), 17)
        self.assertGreater(sensitivity[0][1], sensitivity[-1][1])
        self.assertIn('Références', wb.sheetnames)
        self.assertIn('Méthode et limites', wb.sheetnames)

    def test_cli_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'input.json'
            output = Path(tmp) / 'nested/report.xlsx'
            config.write_text(json.dumps(asdict(DEFAULT)))
            main(['--inputs', str(config), '--output', str(output)])
            self.assertTrue(output.exists())

    def test_invalid_numbers(self):
        for field, value in [('principal', float('inf')), ('rate', float('nan')),
                             ('years', 2.5), ('years', True), ('annual_cfads', -1),
                             ('coverage', 1.1), ('annual_interest', '0.05')]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                build_workbook(replace(DEFAULT, **{field: value}))

    def test_rejected_input_leaves_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / 'bad.json'
            output = Path(tmp) / 'report.xlsx'
            config.write_text(json.dumps(asdict(replace(DEFAULT, depreciation=1))))
            with self.assertRaises(SystemExit):
                main(['--inputs', str(config), '--output', str(output)])
            self.assertFalse(output.exists())
