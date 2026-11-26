import unittest
from dataclasses import replace
from model import Inputs, simulate

class SimulationTests(unittest.TestCase):
    def setUp(self):
        self.x = Inputs(100, .1, 2, 2, 180, .2, 0, 2, 0)

    def test_amortization_and_shock(self):
        r = simulate(self.x)
        self.assertEqual([x['Principal (devise)'] for x in r], [50, 50])
        self.assertEqual(r[0]['Taux scénario'], 2.5)
        self.assertEqual(r[0]['Service sans couverture (local)'], 150)
        self.assertAlmostEqual(r[0]['DSCR sans couverture'], 1.2)

    def test_hedging(self):
        r = simulate(replace(self.x, coverage=.5, annual_cost_rate=.1))[0]
        self.assertEqual(r['Service avec couverture (local)'], 141)
        self.assertEqual(r['Coût couverture (local)'], 6)

    def test_invalid(self):
        for x in (replace(self.x, depreciation=1), replace(self.x, years=0), replace(self.x, rate=0)):
            with self.assertRaises(ValueError):
                simulate(x)

if __name__ == '__main__':
    unittest.main()
