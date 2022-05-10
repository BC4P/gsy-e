def get_setup(config):
    area = Area(
        "Grid",
        [
            Area(
                "FH Campus",
                [
                    Area("H2 General Load",
                         strategy=DefinedLoadStrategy(
                             daily_load_profile=os.path.join(d3a_path,
                                                             "resources",
                                                             "out.csv"),
                             final_buying_rate=35),
                         ),
                ]
            ),
            Area(
                "House 1",
                [
                    Area("H1 General Load", strategy=LoadHoursStrategy(avg_power_W=200,
                                                                       hrs_per_day=6,
                                                                       hrs_of_day=list(
                                                                           range(12, 18)),
                                                                       final_buying_rate=35)
                         ),
                    Area("H1 Storage1", strategy=StorageStrategy(initial_soc=50)
                         ),
                    Area("H1 Storage2", strategy=StorageStrategy(initial_soc=50)
                         ),
                ],
                grid_fee_percentage=0, grid_fee_constant=0,
            ),
            Area(
                "House 2",
                [
                    Area("H2 General Load", strategy=LoadHoursStrategy(avg_power_W=200,
                                                                       hrs_per_day=4,
                                                                       hrs_of_day=list(
                                                                           range(12, 16)),
                                                                       final_buying_rate=35)
                         ),
                    Area("H2 PV", strategy=PVStrategy(capacity_kW=0.16,
                                                      panel_count=4,
                                                      initial_selling_rate=30,
                                                      final_selling_rate=5)
                         ),

                ],
                grid_fee_percentage=0, grid_fee_constant=0,

            ),
            Area("Commercial Energy Producer",
                 strategy=CommercialStrategy(energy_rate=30)
            ),
            # Area("DSO",
            #      strategy=InfiniteBusStrategy(energy_buy_rate=1000, energy_sell_rate=30)
            # ),
        ],
        config=config
    )
    return area
