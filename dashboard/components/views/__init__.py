"""
ECDAT Dashboard Views — Nova Edition.
"""
from .asset_intelligence import render_asset_intelligence
from .blind_spots import render_blind_spots_and_risk
from .cbom_compliance import render_cbom_and_compliance
from .discovery import render_discovery
from .evidence_graph import render_evidence_graph
from .migration_simulator import render_migration_and_simulator
from .overview import render_overview

__all__ = [
    "render_asset_intelligence",
    "render_blind_spots_and_risk",
    "render_cbom_and_compliance",
    "render_discovery",
    "render_evidence_graph",
    "render_migration_and_simulator",
    "render_overview",
]
