# flake8: noqa

import os
import platform

from gsy_e.models.area import Area
from gsy_framework.constants_limits import ConstSettings
from gsy_framework.enums import SpotMarketTypeEnum, BidOfferMatchAlgoEnum
from gsy_e.models.strategy.infinite_bus import InfiniteBusStrategy
from gsy_e.models.strategy.external_strategies.pv import PVUserProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.load import LoadProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.storage import StorageExternalStrategy
from gsy_e.models.strategy.load_hours import LoadHoursStrategy
from gsy_e.models.strategy.pv import PVStrategy

current_dir = os.path.dirname(__file__)
print(current_dir)
print(platform.python_implementation())


# PV production profile was generated with Energy Data Map https://energydatamap.com/
# Load consumption profiles were generated with Load Profile Generator https://www.loadprofilegenerator.de/

def get_setup(config):

    ConstSettings.MASettings.MARKET_TYPE = 2#SpotMarketTypeEnum.TWO_SIDED
    ConstSettings.MASettings.BID_OFFER_MATCH_TYPE = 1#BidOfferMatchAlgoEnum.PAY_AS_BID


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
                                                                 "resources/CHR15 Multigenerational Home working couple, 2 children, 2 seniors HH1.csv"),
                                 initial_buying_rate=11,
                                 use_market_maker_rate=True),
                                  ),
                            Area("PV 5 (10kW)", strategy=PVStrategy(4,
                                                      initial_selling_rate=30,
                                                      final_selling_rate=0,
                                                      fit_to_limit=True,
                                                      update_interval=1),
                                  ),

                         ]),

                ], grid_fee_constant=4, external_connection_available=True),
        ],
        config=config, grid_fee_constant=4, external_connection_available=True
    )
    return area
