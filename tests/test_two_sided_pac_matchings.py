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
import unittest
import pendulum
from parameterized import parameterized
from d3a.models.market.market_structures import Bid, Offer, BidOfferMatch, Trade
from d3a.models.market.two_sided import TwoSidedMarket
from d3a.models.myco_matcher.pay_as_clear import PayAsClear


class TestCreateBidOfferMatchings(unittest.TestCase):

    def validate_matching(self, matching, matched_energy, offer_id, bid_id):
        assert matching.offer_energy == matched_energy
        assert matching.offer.id == offer_id
        assert matching.bid_energy == matched_energy
        assert matching.bid.id == bid_id

    @parameterized.expand([
        (1, 2, 3, 4, 5, 15),
        (5, 4, 3, 2, 1, 15),
        (12, 123, 432, 543, 1, 1111.2),
        (867867.61, 123.98, 432.43, 12.12, 0.001, 868440)
    ])
    def test_create_bid_offer_matchings_respects_offer_bid_order(
            self, en1, en2, en3, en4, en5, clearing_energy
    ):
        bid_list = [
            Bid('bid_id', pendulum.now(), 1, en1, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 2, en2, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, en3, 'B', 'S'),
            Bid('bid_id3', pendulum.now(), 4, en4, 'B', 'S'),
            Bid('bid_id4', pendulum.now(), 5, en5, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 1, en1, 'S'),
            Offer('offer_id1', pendulum.now(), 2, en2, 'S'),
            Offer('offer_id2', pendulum.now(), 3, en3, 'S'),
            Offer('offer_id3', pendulum.now(), 4, en4, 'S'),
            Offer('offer_id4', pendulum.now(), 5, en5, 'S')
        ]

        matchings = PayAsClear._create_bid_offer_matchings(
            (1, clearing_energy), offer_list, bid_list
        )

        assert len(matchings) == 5
        self.validate_matching(matchings[0], en1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], en2, 'offer_id1', 'bid_id1')
        self.validate_matching(matchings[2], en3, 'offer_id2', 'bid_id2')
        self.validate_matching(matchings[3], en4, 'offer_id3', 'bid_id3')
        self.validate_matching(matchings[4], en5, 'offer_id4', 'bid_id4')

    def test_create_bid_offer_matchings_can_handle_partial_bids(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 9, 9, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 3, 3, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, 3, 'B', 'S'),
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 1, 1, 'S'),
            Offer('offer_id1', pendulum.now(), 2, 2, 'S'),
            Offer('offer_id2', pendulum.now(), 3, 3, 'S'),
            Offer('offer_id3', pendulum.now(), 4, 4, 'S'),
            Offer('offer_id4', pendulum.now(), 5, 5, 'S')
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        assert len(matchings) == 7
        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id1', 'bid_id')
        self.validate_matching(matchings[2], 3, 'offer_id2', 'bid_id')
        self.validate_matching(matchings[3], 3, 'offer_id3', 'bid_id')
        self.validate_matching(matchings[4], 1, 'offer_id3', 'bid_id1')
        self.validate_matching(matchings[5], 2, 'offer_id4', 'bid_id1')
        self.validate_matching(matchings[6], 3, 'offer_id4', 'bid_id2')

    def test_create_bid_offer_matchings_can_handle_partial_offers(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 2, 2, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, 3, 'B', 'S'),
            Bid('bid_id3', pendulum.now(), 4, 4, 'B', 'S'),
            Bid('bid_id4', pendulum.now(), 5, 5, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 8, 8, 'S'),
            Offer('offer_id1', pendulum.now(), 4, 4, 'S'),
            Offer('offer_id2', pendulum.now(), 3, 3, 'S'),
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id', 'bid_id1')
        self.validate_matching(matchings[2], 3, 'offer_id', 'bid_id2')
        self.validate_matching(matchings[3], 2, 'offer_id', 'bid_id3')
        self.validate_matching(matchings[4], 2, 'offer_id1', 'bid_id3')
        self.validate_matching(matchings[5], 2, 'offer_id1', 'bid_id4')
        self.validate_matching(matchings[6], 3, 'offer_id2', 'bid_id4')

    def test_create_bid_offer_matchings_can_handle_excessive_offer_energy(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 2, 2, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, 3, 'B', 'S'),
            Bid('bid_id3', pendulum.now(), 4, 4, 'B', 'S'),
            Bid('bid_id4', pendulum.now(), 5, 5, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 8, 8, 'S'),
            Offer('offer_id1', pendulum.now(), 4, 4, 'S'),
            Offer('offer_id2', pendulum.now(), 13, 13, 'S'),
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        assert len(matchings) == 7
        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id', 'bid_id1')
        self.validate_matching(matchings[2], 3, 'offer_id', 'bid_id2')
        self.validate_matching(matchings[3], 2, 'offer_id', 'bid_id3')
        self.validate_matching(matchings[4], 2, 'offer_id1', 'bid_id3')
        self.validate_matching(matchings[5], 2, 'offer_id1', 'bid_id4')
        self.validate_matching(matchings[6], 3, 'offer_id2', 'bid_id4')

    def test_create_bid_offer_matchings_can_handle_excessive_bid_energy(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 2, 2, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, 3, 'B', 'S'),
            Bid('bid_id3', pendulum.now(), 4, 4, 'B', 'S'),
            Bid('bid_id4', pendulum.now(), 5, 5, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 8, 8, 'S'),
            Offer('offer_id1', pendulum.now(), 4, 4, 'S'),
            Offer('offer_id2', pendulum.now(), 5003, 5003, 'S'),
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        assert len(matchings) == 7
        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id', 'bid_id1')
        self.validate_matching(matchings[2], 3, 'offer_id', 'bid_id2')
        self.validate_matching(matchings[3], 2, 'offer_id', 'bid_id3')
        self.validate_matching(matchings[4], 2, 'offer_id1', 'bid_id3')
        self.validate_matching(matchings[5], 2, 'offer_id1', 'bid_id4')
        self.validate_matching(matchings[6], 3, 'offer_id2', 'bid_id4')

    def test_create_bid_offer_matchings_can_match_with_only_one_offer(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'),
            Bid('bid_id1', pendulum.now(), 2, 2, 'B', 'S'),
            Bid('bid_id2', pendulum.now(), 3, 3, 'B', 'S'),
            Bid('bid_id3', pendulum.now(), 4, 4, 'B', 'S'),
            Bid('bid_id4', pendulum.now(), 5, 5, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 8, 800000000, 'S')
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        assert len(matchings) == 5
        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id', 'bid_id1')
        self.validate_matching(matchings[2], 3, 'offer_id', 'bid_id2')
        self.validate_matching(matchings[3], 4, 'offer_id', 'bid_id3')
        self.validate_matching(matchings[4], 5, 'offer_id', 'bid_id4')

    def test_create_bid_offer_matchings_can_match_with_only_one_bid(self):
        bid_list = [
            Bid('bid_id', pendulum.now(), 9, 90123456789, 'B', 'S')
        ]

        offer_list = [
            Offer('offer_id', pendulum.now(), 1, 1, 'S'),
            Offer('offer_id1', pendulum.now(), 2, 2, 'S'),
            Offer('offer_id2', pendulum.now(), 3, 3, 'S'),
            Offer('offer_id3', pendulum.now(), 4, 4, 'S'),
            Offer('offer_id4', pendulum.now(), 5, 5, 'S')
        ]

        matchings = PayAsClear._create_bid_offer_matchings((1, 15), offer_list, bid_list)

        assert len(matchings) == 5
        self.validate_matching(matchings[0], 1, 'offer_id', 'bid_id')
        self.validate_matching(matchings[1], 2, 'offer_id1', 'bid_id')
        self.validate_matching(matchings[2], 3, 'offer_id2', 'bid_id')
        self.validate_matching(matchings[3], 4, 'offer_id3', 'bid_id')
        self.validate_matching(matchings[4], 5, 'offer_id4', 'bid_id')

    def test_matching_list_gets_updated_with_residual_offers(self):
        matchings = [
            BidOfferMatch(offer=Offer('offer_id', pendulum.now(), 1, 1, 'S'), offer_energy=1,
                          bid=Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'), bid_energy=1,
                          trade_rate=1),
            BidOfferMatch(offer=Offer('offer_id2', pendulum.now(), 2, 2, 'S'), offer_energy=2,
                          bid=Bid('bid_id2', pendulum.now(), 2, 2, 'B', 'S'), bid_energy=2,
                          trade_rate=1)
        ]

        offer_trade = Trade('trade', 1, Offer('offer_id', pendulum.now(), 1, 1, 'S'), 'S', 'B',
                            residual=Offer('residual_offer', pendulum.now(), 0.5, 0.5, 'S'))
        bid_trade = Trade('bid_trade', 1, Bid('bid_id2', pendulum.now(), 1, 1, 'S', 'B'), 'S', 'B',
                          residual=Bid('residual_bid_2', pendulum.now(), 1, 1, 'S', 'B'))

        matchings = TwoSidedMarket._replace_offers_bids_with_residual_in_matching_list(
            matchings, 0, offer_trade, bid_trade
        )
        assert len(matchings) == 2
        assert matchings[0].offer.id == 'residual_offer'
        assert matchings[1].bid.id == 'residual_bid_2'

    def test_matching_list_affects_only_matches_after_start_index(self):
        matchings = [
            BidOfferMatch(offer=Offer('offer_id', pendulum.now(), 1, 1, 'S'), offer_energy=1,
                          bid=Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'), bid_energy=1,
                          trade_rate=1),
            BidOfferMatch(offer=Offer('offer_id2', pendulum.now(), 2, 2, 'S'), offer_energy=2,
                          bid=Bid('bid_id2', pendulum.now(), 2, 2, 'B', 'S'), bid_energy=2,
                          trade_rate=1),
            BidOfferMatch(offer=Offer('offer_id', pendulum.now(), 1, 1, 'S'), offer_energy=1,
                          bid=Bid('bid_id', pendulum.now(), 1, 1, 'B', 'S'), bid_energy=1,
                          trade_rate=1)
        ]

        offer_trade = Trade('trade', 1, Offer('offer_id', pendulum.now(), 1, 1, 'S'), 'S', 'B',
                            residual=Offer('residual_offer', pendulum.now(), 0.5, 0.5, 'S'))
        bid_trade = Trade('bid_trade', 1, Bid('bid_id2', pendulum.now(), 1, 1, 'S', 'B'), 'S', 'B',
                          residual=Bid('residual_bid_2', pendulum.now(), 1, 1, 'S', 'B'))

        matchings = TwoSidedMarket._replace_offers_bids_with_residual_in_matching_list(
            matchings, 1, offer_trade, bid_trade
        )
        assert len(matchings) == 3
        assert matchings[0].offer.id == 'offer_id'
        assert matchings[1].bid.id == 'residual_bid_2'
        assert matchings[2].offer.id == 'residual_offer'
