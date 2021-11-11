"""
Copyright 2018 Grid Singularity
This file is part of Grid Singularity Exchange.

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
from collections import OrderedDict
from typing import Dict, TYPE_CHECKING, Optional, List

from gsy_framework.constants_limits import ConstSettings, TIME_FORMAT
from gsy_framework.enums import SpotMarketTypeEnum
from pendulum import DateTime

from gsy_e.gsy_e_core.util import is_time_slot_in_simulation_duration
from gsy_e.models.area.market_rotators import (BaseRotator, DefaultMarketRotator,
                                               SettlementMarketRotator, FutureMarketRotator)
from gsy_e.models.market import GridFee, Market
from gsy_e.models.market.balancing import BalancingMarket
from gsy_e.models.market.future import FutureMarkets
from gsy_e.models.market.market_structures import AvailableMarketTypes
from gsy_e.models.market.one_sided import OneSidedMarket
from gsy_e.models.market.settlement import SettlementMarket
from gsy_e.models.market.two_sided import TwoSidedMarket

if TYPE_CHECKING:
    from gsy_e.models.area import Area


class AreaMarkets:
    """Class that holds all markets for areas."""
    # pylint: disable = too-many-instance-attributes

    def __init__(self, area_log):
        self.log = area_log
        # Children trade in `markets`
        self.markets:  Dict[DateTime, Market] = OrderedDict()
        self.balancing_markets:  Dict[DateTime, BalancingMarket] = OrderedDict()
        self.settlement_markets: Dict[DateTime, TwoSidedMarket] = OrderedDict()
        # Past markets:
        self.past_markets:  Dict[DateTime, Market] = OrderedDict()
        self.past_balancing_markets:  Dict[DateTime, BalancingMarket] = OrderedDict()
        self.past_settlement_markets: Dict[DateTime, TwoSidedMarket] = OrderedDict()
        # TODO: rename and refactor in the frame of D3ASIM-3633:
        self.indexed_future_markets = {}
        # Future markets:
        self.future_markets: Optional[FutureMarkets] = None

        self._spot_market_rotator = BaseRotator()
        self._balancing_market_rotator = BaseRotator()
        self._settlement_market_rotator = BaseRotator()
        self._future_market_rotator = BaseRotator()

        self.spot_market_ids: List = []
        self.balancing_market_ids: List = []
        self.settlement_market_ids: List = []

    def update_area_market_id_lists(self) -> None:
        """Populate lists of market-ids that are currently in the market dicts."""
        self.spot_market_ids: List = [market.id
                                      for market in self.markets.values()]
        self.balancing_market_ids: List = [market.id
                                           for market in self.balancing_markets.values()]
        self.settlement_market_ids: List = [market.id
                                            for market in self.settlement_markets.values()]

    def activate_future_markets(self, area: "Area") -> None:
        """
        Create FutureMarkets instance and create IAAs that communicate to the parent FutureMarkets
        """
        market = FutureMarkets(
            bc=area.bc,
            notification_listener=area.dispatcher.broadcast_notification,
            grid_fee_type=area.config.grid_fee_type,
            grid_fees=GridFee(grid_fee_percentage=area.grid_fee_percentage,
                              grid_fee_const=area.grid_fee_constant),
            name=area.name)
        self.future_markets = market
        area.dispatcher.create_area_agents_for_future_markets(market)

    def activate_market_rotators(self):
        """The user specific ConstSettings are not available when the class is constructed,
        so we need to have a two-stage initialization here."""
        self._spot_market_rotator = DefaultMarketRotator(self.markets, self.past_markets)
        if ConstSettings.BalancingSettings.ENABLE_BALANCING_MARKET:
            self._balancing_market_rotator = (
                DefaultMarketRotator(self.balancing_markets, self.past_balancing_markets))
        if ConstSettings.SettlementMarketSettings.ENABLE_SETTLEMENT_MARKETS:
            self._settlement_market_rotator = (
                SettlementMarketRotator(self.settlement_markets, self.past_settlement_markets))
        if self.future_markets:
            self._future_market_rotator = FutureMarketRotator(self.future_markets)

    def _update_indexed_future_markets(self) -> None:
        """Update the indexed_future_markets mapping."""
        self.indexed_future_markets = {m.id: m for m in self.markets.values()}

    def rotate_markets(self, current_time: DateTime) -> None:
        """Deal with market rotation of different types."""
        self._spot_market_rotator.rotate(current_time)
        self._balancing_market_rotator.rotate(current_time)
        self._settlement_market_rotator.rotate(current_time)
        self._future_market_rotator.rotate(current_time)

        self._update_indexed_future_markets()

    @staticmethod
    def _select_market_class(market_type: AvailableMarketTypes) -> type(Market):
        """Select market class dependent on the global config."""
        if market_type == AvailableMarketTypes.SPOT:
            if ConstSettings.IAASettings.MARKET_TYPE == SpotMarketTypeEnum.ONE_SIDED.value:
                return OneSidedMarket
            if ConstSettings.IAASettings.MARKET_TYPE == SpotMarketTypeEnum.TWO_SIDED.value:
                return TwoSidedMarket
        if market_type == AvailableMarketTypes.SETTLEMENT:
            return SettlementMarket
        if market_type == AvailableMarketTypes.BALANCING:
            return BalancingMarket

        assert False, f"Market type not supported {market_type}"

    def get_market_instances_from_class_type(self, market_type: AvailableMarketTypes) -> Dict:
        """Select market dict based on the market class type."""
        if market_type == AvailableMarketTypes.SPOT:
            return self.markets
        if market_type == AvailableMarketTypes.SETTLEMENT:
            return self.settlement_markets
        if market_type == AvailableMarketTypes.BALANCING:
            return self.balancing_markets

        assert False, f"Market type not supported {market_type}"

    def create_new_spot_market(self, current_time: DateTime,
                               market_type: AvailableMarketTypes, area: "Area") -> bool:
        """Create future markets according to the market count."""
        markets = self.get_market_instances_from_class_type(market_type)
        market_class = self._select_market_class(market_type)

        changed = False
        if not markets or current_time not in markets:
            markets[current_time] = self._create_market(
                market_class, current_time, area, market_type)
            changed = True
            self.log.trace("Adding %s market", current_time.format(TIME_FORMAT))
        self._update_indexed_future_markets()
        return changed

    def create_settlement_market(self, time_slot: DateTime, area: "Area") -> None:
        """Create a new settlement market."""
        self.settlement_markets[time_slot] = (
            self._create_market(market_class=SettlementMarket,
                                time_slot=time_slot,
                                area=area, market_type=AvailableMarketTypes.SETTLEMENT))
        self.log.trace("Adding %s market", time_slot.format(TIME_FORMAT))

    @staticmethod
    def _create_market(market_class: Market,
                       time_slot: DateTime, area: "Area",
                       market_type: AvailableMarketTypes) -> Market:
        """Create market for specific time_slot and market type."""
        market = market_class(
            time_slot=time_slot,
            bc=area.bc,
            notification_listener=area.dispatcher.broadcast_notification,
            grid_fee_type=area.config.grid_fee_type,
            grid_fees=GridFee(grid_fee_percentage=area.grid_fee_percentage,
                              grid_fee_const=area.grid_fee_constant),
            name=area.name,
            in_sim_duration=is_time_slot_in_simulation_duration(area.config, time_slot)
        )

        area.dispatcher.create_area_agents(market_type, market)
        return market