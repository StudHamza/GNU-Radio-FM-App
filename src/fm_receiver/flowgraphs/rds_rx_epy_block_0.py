"""
FM Station Detector - GNU Radio Embedded Python Block

This block performs automated FM radio station detection by analyzing power spectral 
density data from an FFT-processed RF signal. It identifies active FM broadcast 
stations within the current frequency window and outputs their center frequencies.

Algorithm Overview:
1. Accumulates power measurements across multiple FFT frames for statistical reliability
2. Creates a frequency grid of candidate FM stations spaced 100 kHz apart
3. For each candidate frequency, sums power across FM bandwidth (~200 kHz)
4. Applies threshold-based detection (30% of peak power) to identify active stations
5. Groups adjacent active frequencies to prevent multiple detections of same station
6. Selects peak power frequency within each group as the final station frequency

Parameters:
    fft_size (int): FFT size for frequency resolution (default: 128)
        - Determines frequency bin width: samp_rate / fft_size
        - Larger values provide better frequency resolution but slower processing
    
    samp_rate (float): Sample rate in Hz (default: 2.048e6)
        - Must match the sample rate of input signal
        - Determines the frequency span analyzed: [-samp_rate/2, +samp_rate/2] around center
    
    freq (float): Center frequency in Hz (default: 88e6)
        - The RF center frequency being analyzed
        - Used to calculate absolute frequencies of detected stations
    
    done (int): Processing state flag (default: 0)
        - 0: Continue processing
        - 1: Processing complete, block becomes pass-through

Input:
    - Single input stream of float32 power spectral density values
    - Expected to be magnitude-squared FFT output (power per frequency bin)
    - Requires approximately samp_rate * 2 samples for reliable detection

Output:
    - No streaming output (out_sig=None)
    - Message port "done": Sends completion signal when detection is finished
    - Detected stations accessible via get_stations() method

Key Features:
    - Robust detection using power accumulation over ~2 seconds of data
    - Adjacent channel grouping prevents duplicate station detection
    - Configurable detection threshold for different sensitivity requirements
    - Automatic frequency-to-bin mapping handles arbitrary center frequencies
    - Memory efficient: processes data in chunks and clears buffers when complete

Usage Notes:
    - Designed for FM broadcast band (typically 88-108 MHz)
    - Station spacing assumes 100 kHz channel separation (adjust step_size if needed)
    - FM bandwidth assumption of 200 kHz works for most regions
    - For full-band scanning, use multiple instances with different center frequencies
    - Detection threshold (0.3) may need adjustment based on local signal environment

Example Integration:
    This block is typically placed after an FFT block and complex-to-mag-squared block
    in a GNU Radio flowgraph. Connect the power spectral density output directly to
    this block's input. Monitor the "done" message port to know when detection is complete,
    then call get_stations() to retrieve the list of detected station frequencies.

Performance:
    - Processing time: ~2 seconds of RF data capture + computation time
    - Memory usage: Minimal, processes data in FFT-sized chunks
    - Frequency accuracy: Limited by FFT bin width (~16 kHz for default parameters)

Author: hamza
Version: 1.0
Compatible with: GNU Radio 3.8+
"""

import numpy as np
import math
from gnuradio import gr
import pmt
from time import sleep


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, fft_size=2**7, samp_rate=2.048e6, freq=88e6,done=0):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Embedded Python Block',   # will show up in GRC
            in_sig=[np.float32],
            out_sig=None
        )
        self.done = done
        self.samp_rate = samp_rate  
        self.fft_size = fft_size
        self.freq = freq
        self.threshold =0.3
        self.num_items = samp_rate*2

        bin_bandwidth = samp_rate / fft_size
        fm_bandwidth = 200e3

        station_size = math.ceil(fm_bandwidth / bin_bandwidth)
        self.half_station_size = station_size / 2 if station_size % 2 == 0 else (station_size + 1) / 2
        self.compute_candidate_freqs()

        self.data = np.array([], dtype=np.float32)

        self.power_per_station = np.zeros(self.candidate_freqs.size)

        self.detected_stations= set()

        self.message_port_register_out(pmt.intern("done"))



    def work(self, input_items, output_items):

        if self.done == 1: 
            return len(input_items[0])
        
        self.data = np.concatenate((self.data, input_items[0]))

        if len(self.data) < self.num_items:
            return len(input_items[0])
        
        data = self.data

        self.compute_candidate_freqs() 

        for i in range(0, len(data), self.fft_size):
            if i + self.fft_size > len(data):
                break
                
            data_chunk = data[i:i+self.fft_size]
            
            for j, station_bin in enumerate(self.candidate_freqs_bin):
                start_bin = int(station_bin - self.half_station_size)
                end_bin = int(station_bin + self.half_station_size)
                
                # Ensure we don't go out of bounds
                start_bin = max(0, start_bin)
                end_bin = min(len(data_chunk), end_bin)
                
                if start_bin < end_bin:
                    potential_station = np.sum(np.abs(data_chunk[start_bin:end_bin])**2)
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
        start_freq = self.round_to_3_sigfigs(self.freq -  self.fft_size * (self.samp_rate / self.fft_size) / 2)
        end_freq = self.round_to_3_sigfigs(self.freq +  self.fft_size * (self.samp_rate / self.fft_size) / 2)

        self.candidate_freqs = np.arange(start_freq, end_freq, step_size)
        self.candidate_freqs = self.candidate_freqs[1:-1]
        self.candidate_freqs_bin = np.round(((self.candidate_freqs - self.freq) * self.fft_size / self.samp_rate) + self.fft_size / 2, 1).astype(int)

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

