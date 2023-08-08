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
from gsy_framework.constants_limits import GlobalConfig
from gsy_e.models.strategy.smart_meter import SmartMeterStrategy
from gsy_e.models.strategy.predefined_load import DefinedLoadStrategy
from gsy_e.utils.csv_to_dict import CsvToDict
from gsy_e.gsy_e_core.device_registry import DeviceRegistry
from gsy_e.gsy_e_core.area_serializer import area_to_string, collect_areas_info


from gsy_e.gsy_e_core.util import d3a_path
import os

device_registry = ["B04", 
"B05a",
"B06", 
"B08", 
"B09", 
"B10", 
"B11", 
"B13", 
"B15", 
"B17", 
"B21", 
"B22", 
"B23", 
"B28", 
"B31", 
"B34", 
"B36", 
"B41", 
"B42", 
"B52", 
"B529", 
"Market Maker", 
'Liege']



def get_setup(config):

    #day = "2022-04-09"
    #day = "2022-06-21"
    day = "2022-09-15"

    #DeviceRegistry.REGISTRY_L = device_registry

    area = Area(
        "Grid", 
        [
            Area(
                "Liege",
                [
                    Area("B04", uuid="asset1", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b04.csv"), multiplier=-1000.0))),
                    Area("B05a",uuid="asset2", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b05a.csv"), multiplier=-1000.0))),
                    # Area("B06", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b06.csv"), multiplier=-1000.0))),
                    # Area("B08", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b08.csv"), multiplier=-1000.0))),
                    # Area("B09", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b09.csv"), multiplier=-1000.0))),
                    # Area("B10", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b10.csv"), multiplier=-1000.0))),
                    # Area("B11", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b11.csv"), multiplier=-1000.0))),
                    # Area("B13", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b13.csv"), multiplier=-1000.0))),
                    # Area("B15", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b15.csv"), multiplier=-1000.0))),
                    # Area("B17", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b17.csv"), multiplier=-1000.0))),
                    # Area("B21", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b21.csv"), multiplier=-1000.0))),
                    # Area("B22", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b22.csv"), multiplier=-1000.0))),
                    # Area("B23", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b23.csv"), multiplier=-1000.0))),
                    # Area("B28", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b28.csv"), multiplier=-1000.0))),
                    # Area("B31", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b31.csv"), multiplier=-1000.0))),
                    # Area("B34", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b34.csv"), multiplier=-1000.0))),
                    # Area("B36", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b36.csv"), multiplier=-1000.0))),
                    # Area("B41", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b41.csv"), multiplier=-1000.0))),
                    # Area("B42", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b42.csv"), multiplier=-1000.0))),
                    # Area("B52", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b52.csv"), multiplier=-1000.0))),
                    # Area("B529", strategy=SmartMeterStrategy(smart_meter_profile=CsvToDict.convert(path=os.path.join(d3a_path,"resources","liege",day,"b529.csv"), multiplier=-1000.0))),
                ],
                uuid="liege"
            ),
            Area("Market Maker",uuid="marketMaker", strategy=InfiniteBusStrategy(energy_buy_rate=10, energy_sell_rate=30)),
        ],
        uuid="grid",
        config=config,
    )
    print(collect_areas_info(area_to_string(area)))
    DeviceRegistry.REGISTRY_L = collect_areas_info(area_to_string(area))
    return area




# pip install -e .
# gsy-e run --setup bc4p.liege -s 15m --start-date 2022-09-15