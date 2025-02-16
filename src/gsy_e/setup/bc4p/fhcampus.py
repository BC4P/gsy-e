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
from gsy_e.models.strategy.infinite_bus import InfiniteBusStrategy
from gsy_framework.constants_limits import ConstSettings
from gsy_e.models.strategy.database import DatabaseLoadStrategy, DatabasePVStrategy
from gsy_framework.database_connection.connection import InfluxConnection, PostgreSQLConnection
from gsy_framework.database_connection.queries_fhac import QueryFHACAggregated, QueryFHACPV
import gsy_e.constants

def get_setup(config):
    #gsy_e.constants.RUN_IN_REALTIME = True
    connection_psql = PostgreSQLConnection("postgresql_fhaachen.cfg")
    connection_fhaachen = InfluxConnection("influx_fhaachen.cfg")
    # ConstSettings.BalancingSettings.ENABLE_BALANCING_MARKET = True

    area = Area(
        "Grid",
        [
            Area(
                "FH Campus",
                [
                    Area("FH General Load", strategy=DatabaseLoadStrategy(query = QueryFHACAggregated(connection_fhaachen, power_column="P_ges", tablename="Strom"))),
                    Area("FH PV", strategy=DatabasePVStrategy(query = QueryFHACPV(postgresConnection=connection_psql, plant="FP-JUEL", tablename="eview"))),
                ]
            ),
            Area("Market Maker", strategy=InfiniteBusStrategy(energy_buy_rate=10, energy_sell_rate=30)),
        ],
        config=config
    )
    return area


# pip install -e .
# gsy-e run --setup bc4p.fhcampus -s 15m --start-date 2023-05-30