import folium

from mesqual import StudyManager, _kpis_deprecated
from mesqual.units import Units
from mesqual.visualizations.value_mapping_system import SegmentedContinuousColorscale
from mesqual.visualizations.folium_legend_system import ContinuousColorscaleLegend
from mesqual.visualizations.folium_viz_system import (
    PropertyMapper,
    KPIDataItem,
    KPICollectionMapVisualizer,
    AreaGenerator, AreaFeatureResolver,
    TextOverlayGenerator, TextOverlayFeatureResolver,
)
from mesqual.utils.folium_utils.background_color import set_background_color_of_map
from mesqual._kpis_deprecated import KPI

study: StudyManager
(study, )


# Add Country level model
# Add Country level aggregation for price and flows

# three layer categories:
# 1. Model (all overlay = True)
# add countries
# add raw line topology map
# add border topology map
# 2. Prices (all overlay = False)
# None
# all scens / scen changes
# 3. Flows (all overlay = False)
# None
# all scens / scen changes

