"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import math
from time import sleep

import numpy as np
import pmt
from gnuradio import gr


class blk(
    gr.sync_block
):  # other base classes are basic_block, decim_block, interp_block
    """FM Frequency Scanner"""

    def __init__(
        self, fft_size=2**7, samp_rate=2.048e6, freq=88e6, done=0
    ):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name="Embedded Python Block",  # will show up in GRC
            in_sig=[np.float32],
            out_sig=None,
        )
        self.done = done
        self.samp_rate = samp_rate
        self.fft_size = fft_size
        self.freq = freq
        self.threshold = 0.3
        self.num_items = samp_rate * 2

        bin_bandwidth = samp_rate / fft_size
        fm_bandwidth = 200e3

        station_size = math.ceil(fm_bandwidth / bin_bandwidth)
        self.half_station_size = (
            station_size / 2 if station_size % 2 == 0 else (station_size + 1) / 2
        )
        self.compute_candidate_freqs()

        self.data = np.array([], dtype=np.float32)

        self.power_per_station = np.zeros(self.candidate_freqs.size)

        self.detected_stations = set()

        self.message_port_register_out(pmt.intern("done"))

    def work(self, input_items, output_items):

        if self.done == 1:
            return len(input_items[0])

        self.data = np.concatenate((self.data, input_items[0]))

        if len(self.data) < self.num_items:
            return len(input_items[0])

        data = self.data

        self.compute_candidate_freqs()
        print(f"Scannning at {self.freq}")

        for i in range(0, len(data), self.fft_size):
            if i + self.fft_size > len(data):
                break

            data_chunk = data[i : i + self.fft_size]

            for j, station_bin in enumerate(self.candidate_freqs_bin):
                start_bin = int(station_bin - self.half_station_size)
                end_bin = int(station_bin + self.half_station_size)

                # Ensure we don't go out of bounds
                start_bin = max(0, start_bin)
                end_bin = min(len(data_chunk), end_bin)

                if start_bin < end_bin:
                    potential_station = np.sum(
                        np.abs(data_chunk[start_bin:end_bin]) ** 2
                    )
                    self.power_per_station[j] += potential_station

        normalized_power_per_station = self.normalize(self.power_per_station)

        # Find active stations
        active_indices = np.where(normalized_power_per_station > self.threshold)[0]

        # Group adjacent active indices
        groups = []
        if len(active_indices) > 0:
            group = [active_indices[0]]
            for idx in active_indices[1:]:
                if idx == group[-1] + 1:
                    group.append(idx)
                else:
                    groups.append(group)
                    group = [idx]
            groups.append(group)  # append the last group

        # Pick max power freq in each group
        for group in groups:
            max_idx = group[np.argmax(normalized_power_per_station[group])]

            self.detected_stations.add(float(self.candidate_freqs[max_idx]))

        print("Done Scanning")
        self.done = 1
        msg = pmt.cons(pmt.intern("value"), pmt.from_double(1))
        self.message_port_pub(pmt.intern("done"), msg)

        self.clean_up()

        return len(input_items[0])

    def clean_up(self):
        self.power_per_station = np.zeros(self.candidate_freqs.size)
        self.data = np.array([], dtype=np.float32)  # clear data for next batch

    def compute_candidate_freqs(self):
        step_size = 100e3
        start_freq = self.round_to_3_sigfigs(
            self.freq - self.fft_size * (self.samp_rate / self.fft_size) / 2
        )
        end_freq = self.round_to_3_sigfigs(
            self.freq + self.fft_size * (self.samp_rate / self.fft_size) / 2
        )

        self.candidate_freqs = np.arange(start_freq, end_freq, step_size)
        self.candidate_freqs = self.candidate_freqs[1:-1]
        self.candidate_freqs_bin = np.round(
            ((self.candidate_freqs - self.freq) * self.fft_size / self.samp_rate)
            + self.fft_size / 2,
            1,
        ).astype(int)

    def get_staions(self):
        return self.detected_stations

    def normalize(self, x):
        """Normalize array to 0-1 range"""
        x_min, x_max = x.min(), x.max()
        if x_max == x_min:
            return np.zeros_like(x)
        return (x - x_min) / (x_max - x_min)

    def round_to_3_sigfigs(self, x):
        """Round to 3 significant figures"""
        if x == 0:
            return 0
        else:
            return round(x, -int(math.floor(math.log10(abs(x))) - 2))
