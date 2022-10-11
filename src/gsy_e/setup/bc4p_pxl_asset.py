"""
Copyright 2022 BC4P
This file is part of BC4P.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from gsy_e.models.area import Area
from gsy_e.models.strategy.commercial_producer import CommercialStrategy
from gsy_framework.constants_limits import ConstSettings
from gsy_framework.influx_connection.connection import InfluxConnection
from gsy_framework.influx_connection.queries_pxl import DataQueryPXL
from gsy_e.models.strategy.influx import InfluxLoadStrategy, InfluxPVStrategy
from gsy_e.models.strategy.external_strategies.pv import PVUserProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.load import LoadProfileExternalStrategy
from gsy_e.models.strategy.external_strategies.storage import StorageExternalStrategy

# init with zero laod profile

def get_setup(config):
    ConstSettings.GeneralSettings.RUN_IN_REALTIME = True
    connection = InfluxConnection("influx_pxl.cfg")
    tablename = "Total_Electricity"
    zero_path = os.path.join(d3a_path, "resources", "Zero_Curve.csv")

    area = Area(
        "Grid",
        [
            Area(
                "PXL Campus",
                [
                    Area("main_P_L1", strategy=LoadProfileExternalStrategy(daily_load_profile=zero_path, initial_buying_rate=11, use_market_maker_rate=True)),
                    Area("main_P_L2", strategy=LoadProfileExternalStrategy(daily_load_profile=zero_path, initial_buying_rate=11, use_market_maker_rate=True)),
                    Area("main_P_L3", strategy=LoadProfileExternalStrategy(daily_load_profile=zero_path, initial_buying_rate=11, use_market_maker_rate=True)),
                    Area("PV_LS_105A_power", strategy=PVUserProfileExternalStrategy(power_profile=zero_path, panel_count=1, initial_selling_rate=30, final_selling_rate=11)),
                    Area("PV_LS_105B_power", strategy=PVUserProfileExternalStrategy(power_profile=zero_path, panel_count=1, initial_selling_rate=30, final_selling_rate=11)),
                    Area("PV_LS_105E_power", strategy=PVUserProfileExternalStrategy(power_profile=zero_path, panel_count=1, initial_selling_rate=30, final_selling_rate=11)),
                ]
            ),

            Area("Commercial Energy Producer",
                 strategy=CommercialStrategy(energy_rate=30)
                 ),
        ],
        config=config
    )
    return area

# pip install -e .
# gsy-e run --setup bc4p_pxl -s 15m --enable-external-connection --start-date 2022-09-08