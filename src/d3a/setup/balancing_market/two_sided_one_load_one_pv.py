from d3a.models.appliance.switchable import SwitchableAppliance
from d3a.models.area import Area
from d3a.models.strategy.load_hours import LoadHoursStrategy
from d3a.models.appliance.pv import PVAppliance
from d3a.models.strategy.pv import PVStrategy
from d3a.models.const import ConstSettings
from d3a.device_registry import DeviceRegistry


device_registry_dict = {
    "H1 General Load": (32, 35),
}


def get_setup(config):
    # Two sided market
    ConstSettings.IAASettings.MARKET_TYPE = 2
    ConstSettings.PVSettings.MIN_SELLING_RATE = 0
    ConstSettings.GeneralSettings.DEFAULT_MARKET_MAKER_RATE = 30
    ConstSettings.LoadSettings.MIN_ENERGY_RATE = 0
    ConstSettings.LoadSettings.MAX_ENERGY_RATE = 30
    DeviceRegistry.REGISTRY = device_registry_dict
    ConstSettings.BalancingSettings.FLEXIBLE_LOADS_SUPPORT = False
    ConstSettings.BalancingSettings.ENABLE_MARKET = True

    area = Area(
        'Grid',
        [
            Area(
                'House 1',
                [
                    Area('H1 General Load', strategy=LoadHoursStrategy(
                        avg_power_W=200,
                        hrs_per_day=6,
                        hrs_of_day=list(range(9, 15)),
                        min_energy_rate=ConstSettings.LoadSettings.MIN_ENERGY_RATE,
                        max_energy_rate=ConstSettings.LoadSettings.MAX_ENERGY_RATE
                    ), appliance=SwitchableAppliance()),
                ]
            ),
            Area(
                'House 2',
                [
                    Area('H2 PV',
                         strategy=PVStrategy(4, 0),
                         appliance=PVAppliance()
                         ),

                ]
            ),
        ],
        config=config
    )
    return area