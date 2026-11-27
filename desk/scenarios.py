"""Named, dated FX scenarios.

A scenario carries its own exchange-rate regime, so the interface can never show
a bare shock without its label: for a pegged pair (e.g. XAF/EUR) a simulated
depreciation is a *hypothetical parity break*, not an ordinary market move.

No market data, no live quote. Every number here is a didactic assumption the
user can override, and every scenario declares where it comes from.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Regime:
    key: str
    label: str
    #: wording used everywhere the shock is displayed
    shock_label: str
    note: str


REGIMES = {
    "peg": Regime(
        key="peg",
        label="Hard peg",
        shock_label="hypothetical parity break",
        note=(
            "The currency is legally fixed against its anchor. A simulated "
            "depreciation is therefore not an ordinary fluctuation: it is a "
            "break of the parity itself, an institutional event that has "
            "happened in the region but cannot be read off market prices."
        ),
    ),
    "managed": Regime(
        key="managed",
        label="Managed float",
        shock_label="depreciation",
        note=(
            "The central bank leans against the market without defending a "
            "level. Depreciation is a normal, recurring event; its size is a "
            "scenario assumption, not a forecast."
        ),
    ),
    "float": Regime(
        key="float",
        label="Free float",
        shock_label="depreciation",
        note=(
            "The rate is set by the market. Large moves are ordinary events, "
            "but forward prices embed a carry: a cheap-looking hedge usually "
            "means the market already expects the depreciation."
        ),
    ),
}


@dataclass(frozen=True)
class Scenario:
    """A dated, citable starting point for a simulation."""

    key: str
    name: str
    region: str
    regime: str
    #: local currency units per 1 unit of debt currency
    rate: float
    local: str
    foreign: str
    #: illustrative assumptions, all editable in the interface
    principal: float
    years: int
    interest: float
    annual_cfads: float
    depreciation: float
    coverage: float
    forward_rate: float
    annual_cost_rate: float
    #: green side: annual tCO2e avoided / financed by the asset
    co2e_per_year: float
    #: how the green figure was obtained — must never be presented as measured
    co2e_basis: str
    source_note: str

    @property
    def regime_obj(self) -> Regime:
        return REGIMES[self.regime]


SCENARIOS = {
    "xaf-peg-infra": Scenario(
        key="xaf-peg-infra",
        name="CEMAC infrastructure loan",
        region="Central Africa (CEMAC)",
        regime="peg",
        rate=655.957,
        local="XAF",
        foreign="EUR",
        principal=10_000_000.0,
        years=15,
        interest=0.05,
        annual_cfads=850_000_000.0,
        depreciation=0.20,
        coverage=0.50,
        forward_rate=655.957,
        annual_cost_rate=0.0,
        co2e_per_year=12_000.0,
        co2e_basis=(
            "Illustrative order of magnitude for a grid or water asset "
            "(user-supplied, not measured)."
        ),
        source_note=(
            "XAF/EUR parity is a legal fixed rate (1 EUR = 655.957 XAF). Used "
            "here as an assumption of the starting rate, not as a live quote."
        ),
    ),
    "ghs-managed-solar": Scenario(
        key="ghs-managed-solar",
        name="West African solar IPP",
        region="West Africa (Ghana)",
        regime="managed",
        rate=12.5,
        local="GHS",
        foreign="USD",
        principal=25_000_000.0,
        years=18,
        interest=0.07,
        annual_cfads=48_000_000.0,
        depreciation=0.30,
        coverage=0.50,
        forward_rate=15.0,
        annual_cost_rate=0.02,
        co2e_per_year=38_000.0,
        co2e_basis=(
            "Grid emission factor times illustrative annual output; supplied by "
            "the user, not measured."
        ),
        source_note=(
            "GHS is a managed float. Rate, forward and cost are assumption "
            "values chosen to make the mechanism visible, not market prices."
        ),
    ),
    "brl-float-transport": Scenario(
        key="brl-float-transport",
        name="Latin American transport project",
        region="South America (Brazil)",
        regime="float",
        rate=5.4,
        local="BRL",
        foreign="USD",
        principal=40_000_000.0,
        years=12,
        interest=0.09,
        annual_cfads=45_000_000.0,
        depreciation=0.25,
        coverage=0.75,
        forward_rate=6.3,
        annual_cost_rate=0.03,
        co2e_per_year=21_000.0,
        co2e_basis=(
            "Avoided road emissions times illustrative traffic; supplied by the "
            "user, not measured."
        ),
        source_note=(
            "BRL floats. Forward above spot shows the carry a real hedge would "
            "embed; the value is illustrative."
        ),
    ),
}

DEFAULT_SCENARIO = "xaf-peg-infra"


#: five preset shocks, plus 'custom'
SHOCK_PRESETS = [
    (0.00, "No shock"),
    (0.10, "Mild"),
    (0.20, "Moderate"),
    (0.35, "Severe"),
    (0.50, "Extreme"),
]


def get(key: str) -> Scenario:
    return SCENARIOS[key]


def all_scenarios() -> list[Scenario]:
    return list(SCENARIOS.values())
