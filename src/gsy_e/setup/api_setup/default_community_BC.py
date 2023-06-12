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
from gsy_e.models.strategy import BidEnabledStrategy
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
                            Area("Load 5 L9", strategy=LoadHoursStrategy(avg_power_W=100)),
                            Area("PV 5 (10kW)", strategy=BidEnabledStrategy())

                         ]),

                ], grid_fee_constant=4, external_connection_available=True),
        ],
        config=config, grid_fee_constant=4, external_connection_available=True
    )
    return area
