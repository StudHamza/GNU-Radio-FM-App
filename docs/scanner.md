# FM Scanner

The scanner block processes incoming complex baseband samples in real time and performs spectrum analysis to detect active signals. Internally, it applies an FFT over a configurable window size to transform the samples into the frequency domain, computes the power in each frequency bin, and compares the results against detection thresholds to identify occupied channels. Users can configure parameters such as FFT size, sample rate, and center frequency to match their application needs. The block outputs information about detected signals, enabling downstream components to react to spectrum activity.

## Overall Architecture

The system consists of two main components:
1. **fm_scanner.py** - The main GNU Radio flowgraph that handles RF signal acquisition and processing
2. **rds_rx_epy_block_0.py** - An embedded Python block that performs station detection logic

## Main Scanner Flow (fm_scanner.py)

The signal processing pipeline works as follows:

### 1. **Signal Acquisition**
```python
self.soapy_rtlsdr_source_0 = soapy.source(dev, "fc32", 1, 'True', ...)
```
- Uses an RTL-SDR dongle to capture RF signals
- Samples at 2.048 MHz sample rate
- Initially tunes to 87 MHz (start of FM band)
- Captures complex IQ samples

### 2. **Data Limiting**
```python
self.blocks_head_0 = blocks.head(gr.sizeof_gr_complex*1, num_items)
```
- Limits capture to `num_items = samp_rate * 2` samples (about 2 seconds of data)

### 3. **FFT Processing**
```python
self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
```
- Converts stream to vectors of size 128 (2^7)
- Performs FFT with Blackman-Harris windowing
- This converts time-domain samples to frequency domain

### 4. **Power Calculation**
```python
self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)
```
- Converts complex FFT output to power spectral density
- Results in magnitude-squared values representing signal power at each frequency bin

## Station Detection Logic (rds_rx_epy_block_0.py)

This is where the intelligence happens:

### 1. **Initialization Parameters**
- `fft_size = 128`: Frequency resolution
- `samp_rate = 2.048e6`: Sample rate  
- `freq = 88e6`: Center frequency (88 MHz)
- `threshold = 0.3`: Detection threshold (30%)

### 2. **Frequency Grid Calculation**
```python
def compute_candidate_freqs(self):
    step_size = 100e3  # 100 kHz steps
    start_freq = self.round_to_3_sigfigs(self.freq - self.fft_size * (self.samp_rate / self.fft_size) / 2)
    end_freq = self.round_to_3_sigfigs(self.freq + self.fft_size * (self.samp_rate / self.fft_size) / 2)
    self.candidate_freqs = np.arange(start_freq, end_freq, step_size)
```

This creates a grid of candidate station frequencies:
- Covers the bandwidth visible in the current FFT window
- Uses 100 kHz spacing (typical FM channel spacing in many regions)
- Maps frequencies to corresponding FFT bins

### 3. **Power Accumulation**
```python
for j, station_bin in enumerate(self.candidate_freqs_bin):
    start_bin = int(station_bin - self.half_station_size)
    end_bin = int(station_bin + self.half_station_size)
    potential_station = np.sum(np.abs(data_chunk[start_bin:end_bin])**2)
    self.power_per_station[j] += potential_station
```

For each candidate frequency:
- Calculates which FFT bins correspond to that station
- Uses `half_station_size` based on FM bandwidth (200 kHz)
- Sums power across multiple FFT bins for each potential station
- Accumulates power over multiple FFT frames for better statistics

### 4. **Station Detection Algorithm**
```python
normalized_power_per_station = self.normalize(self.power_per_station)
active_indices = np.where(normalized_power_per_station > self.threshold)[0]
```

- Normalizes power measurements to 0-1 range
- Identifies candidates above 30% threshold

### 5. **Adjacent Channel Grouping**
```python
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
```

This clever algorithm:
- Groups adjacent frequency bins that are above threshold
- Prevents detecting the same station multiple times
- Accounts for FM signals spreading across multiple 100kHz channels

### 6. **Peak Selection**
```python
for group in groups:
    max_idx = group[np.argmax(normalized_power_per_station[group])]
    self.detected_stations.add(float(self.candidate_freqs[max_idx]))
```
- For each group of adjacent active channels
- Selects the frequency with maximum power as the actual station frequency

## Key Design Features

1. **Frequency Resolution**: With 128-point FFT and 2.048 MHz sample rate, each bin represents ~16 kHz
2. **Station Bandwidth**: Assumes 200 kHz FM bandwidth, covering multiple FFT bins per station
3. **Robust Detection**: Uses power accumulation over time and adjacent channel grouping
4. **Threshold-based**: Only reports stations above 30% of the maximum detected power

## Limitations & Observations

1. **Fixed Frequency**: Currently only scans around 88 MHz - would need frequency hopping for full FM band
2. **Single Capture**: Takes one 2-second snapshot rather than continuous scanning
3. **Simple Threshold**: Uses basic power thresholding rather than more sophisticated detection algorithms

This is a solid foundation for an FM scanner that could be extended to sweep the entire FM band (88-108 MHz) by iterating through different center frequencies.