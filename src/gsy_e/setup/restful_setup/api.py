import time
from gsy_e.models.area import Area
from gsy_e.models.strategy.external_strategies.load import LoadProfileExternalStrategy
from gsy_e.models.strategy.load_hours import LoadHoursStrategy
from gsy_e_sdk.setups.asset_api_scripts.redis_basic_strategies_BC import Oracle, register_asset_list
import subprocess
import threading
import queue
import threading
import uuid
import redis

import pickle

import json

import asyncio
from flask import Flask,current_app
from flask import request
from flask_socketio import SocketIO, emit
import os
import eventlet

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
p = redis_client.pubsub()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug = True

current_dir = os.path.dirname(__file__)
socketio = SocketIO(app, async_mode='eventlet')
eventlet.monkey_patch()

# asset_args = {"autoregister": True, "pubsub_thread": aggregator.pubsub}
strategies = {
    'LoadProfileExternalStrategy':LoadProfileExternalStrategy,
    'LoadHoursStrategy':LoadHoursStrategy
}

simulation_threads = {}
simulations = {}
oracles = {}
lock = threading.Lock()



def areaDecoder(areaDict):
    children = []

    if "children" in areaDict:
        for child in areaDict['children']:
            children.append(areaDecoder(child))

    strategy = None
    if "strategy" in areaDict:
        strategyClassStr = areaDict['strategy']['class']
        strategyClass = strategies[strategyClassStr]
        strategyArgs = areaDict['strategy']['args']
        print(strategyArgs)
        strategy = strategyClass(**strategyArgs)
    area = Area(
        areaDict['name'],
        children=children,
        grid_fee_constant=areaDict.get('grid_fee_constant'), 
        external_connection_available=areaDict.get('external_connection_available'),
        strategy = strategy
    )
    return area

@app.route("/load_setup")
def load_setup():
    areaJson = request.json
    area = areaDecoder(areaJson)
    print(area)
    file_name = './preloaded_setups/'+area.name+'.pkl'
    with open(file_name, 'wb') as file:
        pickle.dump(area, file)
        print(f'Object successfully saved to "{file_name}"')
    print(area)
    return area.name
    
@app.route('/oracle/count')
def count_oracles():
    return str(oracles)


@app.route("/register_assets") 
def register_assets():
    t = threading.Thread(target=run_oracle)
    t.start()
    return 'oracle started'


@app.route("/run_simulation")
def run_simulation():
    new_simulation = Simulation(lock)
    new_simulation.start()
    return 'done'

@app.route("/stop_simulation")
def stop_simulation():
    simulation = list(simulations.values())[0]
    simulation.stop()
    print(simulation.info)
    return simulation.info

@app.route('/count_simulations')
def count():
    print("simulation,  ", simulations)
    print(Simulation.all_threads)
    return {str(k):str(v.info) for k,v in simulations.items()}

@app.route('/simulation/command')
def command():
    simulation = list(simulations.values())[0]
    command = request.args.get("cmd")
    simulation.add_cmd(command)
    return request.args




@socketio.on('connect')
def on_connect():
    print("connecting to simulation-socket")

@socketio.on('start_simulation')
def start_simulation(data):
    print('simulation-started')

@socketio.on('simulation_output')
def start_simulation(data):
    print('simulation output')

@socketio.on('simulation_ended')
def start_simulation(data):
    print('simulation_ended')












class RedisThread(threading.Thread):
    
    def __init__(self, redisClient:redis.Redis, channels):
        threading.Thread.__init__(self, name="Redis listener thread")

        self._stop_event = threading.Event()
        self.redis = redisClient
        print(self.redis.ping())
        self.pubsub = redisClient.pubsub()
        for channel in channels:
            self.pubsub.psubscribe(channel)
    def run(self):
        print("running redis thread")
        while not self._stop_event.is_set():
            for message in self.pubsub.listen():
                pattern = message['pattern']
                socketio.emit(pattern, message["data"])
                print('channel: {} message: {}'.format(pattern, message["data"]))
            time.sleep(0.2)

    def stop(self):
        self._stop_event.set()



class Simulation(threading.Thread):
    all_threads = []
    def __init__(self,*args):
        threading.Thread.__init__(self, name="Simulation thread")
        self.id = uuid.uuid4()
        self.queue = []
        simulations[self.id] = self
        self._stop_event = threading.Event()
        self.process = None
        self.info={
            "is running":False
        }
        self.all_threads.append(self)
        self.args = args

        

    def run(self):
        print(self.args)
        lock = self.args[0]
        cmd_string = 'gsy-e -l INFO run -t 5s -s 15m --setup "./preloaded_setups/Grid.pkl" --enable-external-connection --paused --slot-length-realtime 10'
        self.process = subprocess.Popen("exec " +cmd_string, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(self.process)
        self.info["is running"] = True
        #with app.app_context():
        socketio.emit('start_simulation', 'simulation started')
            #current_app.logger.info("hello")
        while not self._stop_event.is_set():
            if len(self.queue) > 0:
                cmd = self.queue.pop(0)
                if isinstance(cmd, str):
                    # if the command is a string, execute it as a shell command
                    socketio.emit('simulation_command', cmd)
                    subprocess.Popen(cmd)
                elif callable(cmd):
                    # if the command is a callable, call it
                    cmd()
            # try:
            #     lock.acquire()
            #     print(app)
            #     output = self.process.stdout.readline().decode()
            #     if output:
            #         with app.app_context():
            #             socketio.emit('simulation_output', 'simulation ended')
            #     lock.release()
            # except Exception as e:
            #     print("exception: ", e)

            time.sleep(0.2)

        print("TERMINATED   ")
        self.process.kill()
        self.all_threads.remove(self)
        lock.acquire()
        self.info["is running"] = False
        print("PROCESS {}".format(self.process))
        del simulations[self.id]
        lock.release()
        #with app.app_context():
        socketio.emit('simulation_ended', 'simulation ended')



    def add_cmd(self, cmd):
        self.queue.append(cmd)

    def stop(self):
        self._stop_event.set()

def run_oracle():
    try:
        aggregator = Oracle(aggregator_name="ORACLE_NAME")
    except Exception as e:
        socketio.emit('oracle_response', str(e))
        return
    asset_uuid_mapping = {}
    print("aggregator", aggregator)
    asset_args = {"autoregister": True, "pubsub_thread": aggregator.pubsub, 'is_blocking':True}
    asset_uuid_mapping = register_asset_list(["Grid"],asset_args, asset_uuid_mapping, aggregator)
    oracles[aggregator.aggregator_uuid] = aggregator
    print("AGGREGATORS: ",oracles)
    print("oracles response!!!!")
    while not aggregator.is_finished:
        time.sleep(0.5)
    print("finished!!!!")
    socketio.emit('oracle_response', str(asset_uuid_mapping))



# def subscribe_to_redis_channel(channel):
#     pubsub = redis_client.pubsub()
#     pubsub.subscribe(channel)
#     for message in pubsub.listen():
#         handle_redis_message(message['data'])


# @app.before_first_request
# def start_redis_subscription():



# area = areaDecoder(sict_example)
# area.strategy

# print(area.strategy)


if __name__ == '__main__':
    print("lauching redis thread")
    channels = ['*']
    r_thread = RedisThread(redis_client, channels)
    r_thread.start()
    socketio.run(app, debug=True, use_reloader=False)