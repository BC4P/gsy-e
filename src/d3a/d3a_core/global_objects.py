"""
Copyright 2018 Grid Singularity
This file is part of D3A.

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


class GlobalObjects:

    def __init__(self):
        self.area_tree_dict = {}

    def update(self, area):
        self._create_grid_tree_dict(area, self.area_tree_dict)

    def _create_grid_tree_dict(self, area, outdict):
        outdict[area.name] = {"area_grid_fee": area.grid_fee_constant}

        if area.children:
            outdict[area.name].update(
                {"market_bill": area.stats.aggregated_stats,
                 "price_stats": area.market_area.stats.get_price_stats_current_market(),
                 "current_market_fee": str(area.next_market.fee_class.grid_fee_rate),
                 "next_market_fee": str(area.get_grid_fee()),
                 "children": {}})
            for child in area.children:
                self._create_grid_tree_dict(child, outdict[area.name]["children"])
