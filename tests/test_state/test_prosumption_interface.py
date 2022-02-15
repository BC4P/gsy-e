# pylint: disable=protected-access
from unittest.mock import patch, MagicMock
from typing import Dict
import pytest
from pendulum import now, DateTime

from gsy_e.models.state import ProsumptionInterface


class ProsumptionInterfaceHelper(ProsumptionInterface):
    """Helper class to override unimplemented StateInterface's
       abstract methods on ProsumptionInterface class."""

    def get_state(self) -> Dict:
        raise NotImplementedError

    def restore_state(self, state_dict: Dict):
        raise NotImplementedError

    def delete_past_state_values(self, current_time_slot: DateTime):
        raise NotImplementedError


class TestProsumptionInterface:
    """ Test ProsumptionInterface class"""

    @staticmethod
    def _setup_base_configuration():
        return ProsumptionInterfaceHelper(), now()

    def test_set_energy_measurement_kWh_dicts_not_empty(self):
        prosumption_interface, current_time_slot = self._setup_base_configuration()
        energy = 1
        prosumption_interface.set_energy_measurement_kWh(
            energy_kWh=energy, time_slot=current_time_slot
        )
        assert prosumption_interface.get_energy_measurement_kWh(
            time_slot=current_time_slot) == energy
        assert isinstance(prosumption_interface.get_forecast_measurement_deviation_kWh(
            time_slot=current_time_slot), float)
        assert isinstance(prosumption_interface.get_unsettled_deviation_kWh(
            time_slot=current_time_slot), float)

    @staticmethod
    def _setup_configuration_for_settlement_posting(
            energy_deviation=None, unsettled_deviation=None):
        prosumption_interface = ProsumptionInterfaceHelper()
        current_time_slot = now()
        if energy_deviation:
            prosumption_interface._forecast_measurement_deviation_kWh[
                current_time_slot] = energy_deviation
        if unsettled_deviation:
            prosumption_interface._unsettled_deviation_kWh[
                current_time_slot] = unsettled_deviation
        return prosumption_interface, current_time_slot

    @pytest.mark.parametrize(
        "energy_deviation, expected_response", [(None, False), (-1, False), (1, True)])
    def test_can_post_settlement_bid_return_expected(self, energy_deviation, expected_response):
        prosumption_interface, time_slot = self._setup_configuration_for_settlement_posting(
            energy_deviation)
        assert prosumption_interface._forecast_measurement_deviation_kWh.get(
            time_slot) is energy_deviation
        assert prosumption_interface.can_post_settlement_bid(
            time_slot) == expected_response

    @pytest.mark.parametrize(
        "energy_deviation, expected_response", [(None, False), (-1, True), (1, False)])
    def test_can_post_settlement_offer_return_expected(self, energy_deviation, expected_response):
        prosumption_interface, time_slot = self._setup_configuration_for_settlement_posting(
            energy_deviation)
        assert prosumption_interface._forecast_measurement_deviation_kWh.get(
            time_slot) is energy_deviation
        assert prosumption_interface.can_post_settlement_offer(
            time_slot) == expected_response

    @pytest.mark.parametrize(
        "energy_deviation, unsettled_deviation, expected_response",
        [(1, None, None), (None, 1, None), (1, 1, True)])
    def test_get_signed_unsettled_deviation_kWh_return_expected(
            self, energy_deviation, unsettled_deviation, expected_response):
        copysign_mock = MagicMock()
        with patch("gsy_e.models.state.copysign", return_value=copysign_mock):
            prosumption_interface, time_slot = self._setup_configuration_for_settlement_posting(
                energy_deviation=energy_deviation, unsettled_deviation=unsettled_deviation)
            if expected_response:
                assert prosumption_interface.get_signed_unsettled_deviation_kWh(
                    time_slot) == copysign_mock
            else:
                assert prosumption_interface.get_signed_unsettled_deviation_kWh(
                    time_slot) is expected_response

    def test_decrement_unsettled_deviation_decrements_energy(self):
        energy = 1
        prosumption_interface, time_slot = self._setup_configuration_for_settlement_posting(
            unsettled_deviation=4 * energy)
        prosumption_interface.decrement_unsettled_deviation(
            purchased_energy_kWh=energy, time_slot=time_slot)
        prosumption_interface.decrement_unsettled_deviation(
            purchased_energy_kWh=energy, time_slot=time_slot)
        assert prosumption_interface.get_unsettled_deviation_kWh(
            time_slot=time_slot) == 2 * energy

    def test_decrement_unsettled_deviation_raise_error_if_unsettled_energy_is_negative(self):
        energy = 1
        prosumption_interface, time_slot = self._setup_configuration_for_settlement_posting(
            unsettled_deviation=4 * energy)
        with pytest.raises(AssertionError):
            prosumption_interface.decrement_unsettled_deviation(
                purchased_energy_kWh=5*energy, time_slot=time_slot)

    @staticmethod
    def test_get_energy_measurement_kWh():
        time_slot = now()
        prosumption_interface = ProsumptionInterfaceHelper()
        prosumption_interface._energy_measurement_kWh[time_slot] = 123.0
        assert prosumption_interface.get_energy_measurement_kWh(time_slot) == 123

    @staticmethod
    def test_get_forecast_measurement_deviation():
        time_slot = now()
        prosumption_interface = ProsumptionInterfaceHelper()
        prosumption_interface._forecast_measurement_deviation_kWh[time_slot] = 100.0
        assert prosumption_interface.get_forecast_measurement_deviation_kWh(time_slot) == 100

    @staticmethod
    def test_get_unsettled_deviation():
        time_slot = now()
        prosumption_interface = ProsumptionInterfaceHelper()
        prosumption_interface._unsettled_deviation_kWh[time_slot] = 300.0
        assert prosumption_interface.get_unsettled_deviation_kWh(time_slot) == 300
