"""Deterministic annual debt-service stress test. No market data or execution."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Inputs:
    principal: float
    annual_interest: float
    years: int
    rate: float  # local currency per unit of debt currency
    annual_cfads: float  # local currency, assumed constant
    depreciation: float  # fractional drop in value of local currency
    coverage: float  # fraction of each year's debt service notionally covered
    forward_rate: float  # local per foreign unit, user-supplied, not market-priced
    annual_cost_rate: float  # assumed cost as fraction of covered debt service


def simulate(x: Inputs) -> list[dict]:
    if not (x.principal > 0 and 1 <= x.years <= 30 and x.rate > 0 and x.forward_rate > 0):
        raise ValueError('Le principal et les taux de change doivent être positifs ; durée entre 1 et 30 ans.')
    if not (0 <= x.annual_interest <= 1 and 0 <= x.annual_cost_rate <= 1 and x.annual_cfads >= 0):
        raise ValueError('Taux et CFADS hors limites.')
    if not (0 <= x.depreciation < 1 and 0 <= x.coverage <= 1):
        raise ValueError('Dépréciation ou couverture hors limites.')
    stressed_rate = x.rate / (1 - x.depreciation)
    annual_principal = x.principal / x.years
    out = []
    for year in range(1, x.years + 1):
        opening = x.principal - (year - 1) * annual_principal
        interest = opening * x.annual_interest
        service = annual_principal + interest
        uncovered = service * stressed_rate
        cost = service * x.coverage * x.forward_rate * x.annual_cost_rate
        hedged = service * ((1 - x.coverage) * stressed_rate + x.coverage * x.forward_rate) + cost
        out.append({'Année': year, 'Dette initiale (devise)': opening,
                    'Principal (devise)': annual_principal, 'Intérêts (devise)': interest,
                    'Service dette (devise)': service, 'Taux scénario': stressed_rate,
                    'Service sans couverture (local)': uncovered,
                    'Service avec couverture (local)': hedged, 'Coût couverture (local)': cost,
                    'CFADS (local)': x.annual_cfads,
                    'DSCR sans couverture': x.annual_cfads / uncovered,
                    'DSCR avec couverture': x.annual_cfads / hedged})
    return out
