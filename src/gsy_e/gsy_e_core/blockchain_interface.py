from multiprocessing import connection
import uuid
from logging import getLogger
log = getLogger(__name__)

class NonBlockchainInterface:
    def __init__(self, area, simulation_id=None):
        self.market_id = area.uuid
        self.simulation_id = simulation_id
        #print(f"new market created with id: {market_id}")


    def create_new_offer(self, energy, price, seller):
        return str(uuid.uuid4())

    def cancel_offer(self, offer):
        pass

    def change_offer(self, offer, original_offer, residual_offer):
        pass

    def handle_blockchain_trade_event(self, offer, buyer, original_offer, residual_offer):
        return str(uuid.uuid4()), residual_offer

    def track_trade_event(self, time_slot, trade):
        pass

    def bc_listener(self):
        pass

class BC4PBlockchainInterface:

    def __init__(self, area, simulation_id=None):
        import b4p

        if not b4p.started():
            b4p.init()
        
        self.market_id = area.uuid
        self.simulation_id = simulation_id
        account_name = f"{self.market_id}_account"
        b4p.Accounts.new(account_name)

        #area is an Asset
        if area.strategy:
            if area.strategy.is_consumer:
                parent_name = area.parent.uuid
                log.info(f'creating consuming asset\nid: {area.uuid}\naccount: {account_name}\nconnected to {parent_name}')
                b4p.ConsumingAssets.new(area.uuid,account_name,parent_name)
                
            if area.strategy.is_producer:
                parent_name = area.parent.uuid
                log.info(f'creating consuming asset\nid {area.uuid}\naccount: {account_name}\nconnected to {parent_name}')
                b4p.ConsumingAssets.new(area.uuid,account_name,parent_name)
                
        #area is a Market
        else:
            #is the most outer market
            if area.parent == None:
                log.info(f'creating parent market\nid: {area.uuid}\naccount: {account_name}')
                b4p.Markets.new(area.uuid,account_name)
            
            #any other market
            else:
                parent = b4p.Markets[area.parent.uuid]
                log.info(f'creating intermediat market\nid: {area.uuid}\naccount: {account_name}\nconnected to : {parent}')
                b4p.Markets.new(area.uuid,account_name, connection1=parent)
            pass

        #b4p.Markets.new(market_id, "admin")
        #print(f"new market created with id: {market_id}")


    def create_new_offer(self, energy, price, seller):
        import b4p


        print(int(energy))
        print(int(price))
        print(seller)

        return str(uuid.uuid4())

    def cancel_offer(self, offer):
        pass

    def dispatch_offer(self, offer):
        print(offer)
    
    def handle_blockchain_trade_event(self, offer, buyer, original_offer, residual_offer):
        return str(uuid.uuid4()), residual_offer
        

    def change_offer(self, offer, original_offer, residual_offer):
        pass

    def d(self, offer, buyer, original_offer, residual_offer):
        return str(uuid.uuid4()), residual_offer

    def track_trade_event(self, time_slot, trade):
        print(trade)
        pass

    def bc_listener(self):
        pass

def blockchain_interface_factory(should_use_bc, area, simulation_id):
    if not should_use_bc:
        return NonBlockchainInterface(area, simulation_id)
    return BC4PBlockchainInterface(area, simulation_id)
