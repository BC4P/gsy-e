import random
from importlib import import_module
from logging import getLogger

import time
from pathlib import Path
from threading import Event, Thread

import dill
from pendulum import Pendulum
from pendulum.interval import Interval
from pendulum.period import Period
from pickle import HIGHEST_PROTOCOL
from ptpython.repl import embed

from d3a.exceptions import SimulationException
from d3a.models.config import SimulationConfig
# noinspection PyUnresolvedReferences
from d3a import setup as d3a_setup  # noqa
from d3a.util import NonBlockingConsole, format_interval


log = getLogger(__name__)


class _SimulationInterruped(Exception):
    pass


class Simulation:
    def __init__(self, setup_module_name: str, simulation_config: SimulationConfig,
                 slowdown: int = 0, seed=None, paused: bool = False, pause_after: Interval = None,
                 use_repl: bool = False, reset_on_finish: bool = False,
                 reset_on_finish_wait: Interval = Interval(minutes=1), api_url=None):
        self.initial_params = dict(
            slowdown=slowdown,
            seed=seed,
            paused=paused,
            pause_after=pause_after
        )
        self.simulation_config = simulation_config
        self.use_repl = use_repl
        self.reset_on_finish = reset_on_finish
        self.reset_on_finish_wait = reset_on_finish_wait
        self.api_url = api_url
        self.setup_module_name = setup_module_name

        self.run_start = None
        self.paused_time = None

        self._load_setup_module()
        self._init(**self.initial_params)
        self._init_events()

    def _load_setup_module(self):
        try:
            self.setup_module = import_module(".{}".format(self.setup_module_name), 'd3a.setup')
            log.info("Using setup module '%s'", self.setup_module_name)
        except ImportError as ex:
            raise SimulationException(
                "Invalid setup module '{}'".format(self.setup_module_name)) from ex

    def _init_events(self):
        self.interrupt = Event()
        self.interrupted = Event()
        self.ready = Event()
        self.ready.set()

    def _init(self, slowdown, seed, paused, pause_after):
        self.paused = paused
        self.pause_after = pause_after
        self.slowdown = slowdown

        if seed:
            random.seed(seed)

        self.area = self.setup_module.get_setup(self.simulation_config)
        log.info("Starting simulation with config %s", self.simulation_config)
        self.area.activate()

    @property
    def finished(self):
        return self.area.current_tick == self.area.config.total_ticks

    @property
    def time_since_start(self):
        return self.area.current_tick * self.simulation_config.tick_length

    def reset(self, sync=True):
        """
        Reset simulation to initial values and restart the run.

        *IMPORTANT*: This method *MUST* be called from another thread, otherwise a deadlock will
        occur!
        """
        log.error("=" * 15 + " Simulation reset requested " + "=" * 15)
        if sync:
            self.interrupted.clear()
            self.interrupt.set()
            self.interrupted.wait()
            self.interrupt.clear()
        self._init(**self.initial_params)
        self.ready.set()

    def run(self, resume=False) -> (Period, Interval):
        if resume:
            log.critical("Resuming simulation")
            self._info()
        config = self.simulation_config
        tick_lengths_s = config.tick_length.total_seconds()
        slot_count = int(config.duration / config.slot_length) + 1
        while True:
            self.ready.wait()
            self.ready.clear()
            if resume:
                # FIXME: Fix resume time calculation
                if self.run_start is None or self.paused_time is None:
                    raise RuntimeError("Can't resume without saved state")
                slot_resume, tick_resume = divmod(self.area.current_tick, config.ticks_per_slot)
            else:
                self.run_start = Pendulum.now()
                self.paused_time = 0
                slot_resume = tick_resume = 0

            try:
                with NonBlockingConsole() as console:
                    for slot_no in range(slot_resume, config.duration // config.slot_length):
                        log.error(
                            "Slot %d of %d (%2.0f%%)",
                            slot_no + 1,
                            slot_count,
                            (slot_no + 1) / slot_count * 100
                        )

                        for tick_no in range(tick_resume, config.ticks_per_slot):
                            # reset tick_resume after possible resume
                            tick_resume = 0
                            self._handle_input(console)
                            self.paused_time += self._handle_paused(console)
                            tick_start = time.monotonic()
                            log.debug(
                                "Tick %d of %d in slot %d (%2.0f%%)",
                                tick_no + 1,
                                config.ticks_per_slot,
                                slot_no + 1,
                                (tick_no + 1) / config.ticks_per_slot * 100,
                            )
                            self.area.tick()
                            tick_length = time.monotonic() - tick_start
                            if self.slowdown and tick_length < tick_lengths_s:
                                # Simulation runs faster than real time but a slowdown was
                                # requested
                                tick_diff = tick_lengths_s - tick_length
                                diff_slowdown = tick_diff * self.slowdown / 10000
                                log.debug("Slowdown: %.4f", diff_slowdown)
                                self._handle_input(console, diff_slowdown)

                    run_duration = Pendulum.now() - self.run_start
                    paused_duration = Interval(seconds=self.paused_time)

                    log.error(
                        "Run finished in %s%s / %.2fx real time.",
                        run_duration,
                        " ({} paused)".format(paused_duration if paused_duration else ""),
                        config.duration / (run_duration - paused_duration)
                    )
                    log.error("REST-API still running at %s", self.api_url)
                    if self.use_repl:
                        self._start_repl()
                    elif self.reset_on_finish:
                        log.error("Automatically restarting simulation in %s",
                                  format_interval(self.reset_on_finish_wait))
                        self._handle_input(console, self.reset_on_finish_wait.in_seconds())

                        def _reset():
                            self.reset(sync=False)
                            self.paused = False
                        t = Thread(target=_reset)
                        t.start()
                        t.join()
                        continue
                    else:
                        log.info("Ctrl-C to quit")
                        while True:
                            self._handle_input(console, 0.5)

                    break
            except _SimulationInterruped:
                self.interrupted.set()
            except KeyboardInterrupt:
                print("Exiting")
                break

    def toggle_pause(self):
        if self.finished:
            return False
        self.paused = not self.paused
        return True

    def _handle_input(self, console, sleep: float = 0):
        timeout = 0
        start = 0
        if sleep > 0:
            timeout = sleep / 100
            start = time.monotonic()
        while True:
            if self.interrupt.is_set():
                raise _SimulationInterruped()
            cmd = console.get_char(timeout)
            if cmd:
                if cmd not in {'i', 'p', 'q', 'r', 'R', 's', '+', '-'}:
                    log.critical("Invalid command. Valid commands:\n"
                                 "  [i] info\n"
                                 "  [p] pause\n"
                                 "  [q] quit\n"
                                 "  [r] reset\n"
                                 "  [R] start REPL\n"
                                 "  [s] save state\n"
                                 "  [+] increase slowdown\n"
                                 "  [-] decrease slowdown")
                    continue

                if self.finished and cmd in {'p', 'R', '+', '-'}:
                    log.error("Simulation has finished. The commands [p, +, -] are unavailable.")
                    continue

                if cmd == 'r':
                    Thread(target=lambda: self.reset()).start()
                elif cmd == 'R':
                    self._start_repl()
                elif cmd == 'i':
                    self._info()
                elif cmd == 'p':
                    self.paused = not self.paused
                    break
                elif cmd == 'q':
                    raise KeyboardInterrupt()
                elif cmd == 's':
                    self.save_state()
                elif cmd == '+':
                    v = 5
                    if self.slowdown <= 95:
                        self.slowdown += v
                        log.critical("Simulation slowdown changed to %d", self.slowdown)
                elif cmd == '-':
                    if self.slowdown >= 5:
                        self.slowdown -= 5
                        log.critical("Simulation slowdown changed to %d", self.slowdown)
            if sleep == 0 or time.monotonic() - start >= sleep:
                break

    def _handle_paused(self, console):
        if self.pause_after and self.time_since_start >= self.pause_after:
            self.paused = True
            self.pause_after = None
        if self.paused:
            start = time.monotonic()
            log.critical("Simulation paused. Press 'p' to resume or resume from API.")
            while self.paused and not self.interrupt.is_set():
                self._handle_input(console, 0.1)
            log.critical("Simulation resumed")
            return time.monotonic() - start
        return 0

    def _info(self):
        info = self.simulation_config.as_dict()
        slot, tick = divmod(self.area.current_tick, self.simulation_config.ticks_per_slot)
        percent = self.area.current_tick / self.simulation_config.total_ticks * 100
        slot_count = self.simulation_config.duration // self.simulation_config.slot_length
        info.update(slot=slot + 1, tick=tick + 1, slot_count=slot_count, percent=percent)
        log.critical(
            "\n"
            "Simulation configuration:\n"
            "  Duration: %(duration)s\n"
            "  Slot length: %(slot_length)s\n"
            "  Tick length: %(tick_length)s\n"
            "  Market count: %(market_count)d\n"
            "  Ticks per slot: %(ticks_per_slot)d\n"
            "Status:\n"
            "  Slot: %(slot)d / %(slot_count)d\n"
            "  Tick: %(tick)d / %(ticks_per_slot)d\n"
            "  Completed: %(percent).1f%%",
            info
        )

    def _start_repl(self):
        log.info(
            "An interactive REPL has been started. The root Area is available as "
            "`root_area`.")
        log.info("Ctrl-D to quit.")
        embed({'root_area': self.area})

    def save_state(self):
        save_dir = Path('.d3a')
        save_dir.mkdir(exist_ok=True)
        save_file_name = save_dir.joinpath(
            "saved-state_{:%Y%m%dT%H%M%S}.pickle".format(Pendulum.now())
        )
        with save_file_name.open('wb') as save_file:
            dill.dump(self, save_file, protocol=HIGHEST_PROTOCOL)
        log.critical("Saved state to %s", save_file_name.resolve())
        return save_file_name

    def __getstate__(self):
        state = self.__dict__.copy()
        state['_random_state'] = random.getstate()
        del state['interrupt']
        del state['interrupted']
        del state['ready']
        del state['setup_module']
        return state

    def __setstate__(self, state):
        random.setstate(state.pop('_random_state'))
        self.__dict__.update(state)
        self._load_setup_module()
        self._init_events()
