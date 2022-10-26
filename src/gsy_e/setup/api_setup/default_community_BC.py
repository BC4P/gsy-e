# flake8: noqa

import os
import platform

from gsy_e.models.area import Area
from gsy_framework.constants_limits import ConstSettings
from gsy_e.models.strategy.infinite_bus import InfiniteBusStrategy
from gsy_e.models.strategy.external_strategies.pv import PVUserProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.load import LoadProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.storage import StorageExternalStrategy

current_dir = os.path.dirname(__file__)
print(current_dir)
print(platform.python_implementation())


# PV production profile was generated with Energy Data Map https://energydatamap.com/
# Load consumption profiles were generated with Load Profile Generator https://www.loadprofilegenerator.de/


def get_setup(config):

    ConstSettings.GeneralSettings.DEFAULT_UPDATE_INTERVAL = 1
    ConstSettings.MASettings.MARKET_TYPE = 2
    ConstSettings.GeneralSettings.DEFAULT_MARKET_MAKER_RATE = 22

    area = Area(
        "Grid",
        [
            Area(
                "Community",
                [
                   
                    Area("Multigenerational house",
                         [
                             Area("Load 5 L9", strategy=LoadProfileExternalStrategy(
                                 daily_load_profile=os.path.join(current_dir,
                                                                 "resources/CHR15 Multigenerational Home working couple, 2 children, 2   HH1.csv"),
                                 initial_buying_rate=11,
                                 use_market_maker_rate=True),
                                  ),
                             Area("PV 5 (10kW)", strategy=PVUserProfileExternalStrategy(
                                 power_profile=os.path.join(current_dir, "resources/Berlin_pv.csv"),
                                 panel_count=10,
                                 initial_selling_rate=30,
                                 final_selling_rate=11),
                                  ),

                         ]),

                 
                    Area("6 apartments building+PV",
                         [
                             Area("Load 86 L8", strategy=LoadProfileExternalStrategy(
                                 daily_load_profile=os.path.join(current_dir, "resources/CHR11 Student, HH1.csv"),
                                 initial_buying_rate=11,
                                 use_market_maker_rate=True),
                                  ),
                             Area("PV 9 (15kW)", strategy=PVUserProfileExternalStrategy(
                                 power_profile=os.path.join(current_dir, "resources/Berlin_pv.csv"),
                                 panel_count=15,
                                 initial_selling_rate=30,
                                 final_selling_rate=11),
                                  ),
                         ]),

                ], grid_fee_constant=4, external_connection_available=True),

            Area("Market Maker", strategy=InfiniteBusStrategy(energy_buy_rate=21, energy_sell_rate=22)),
        ],
        config=config, grid_fee_constant=4, external_connection_available=True
    )
    return area
