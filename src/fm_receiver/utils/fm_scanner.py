from flowgraphs.fm_scanner import fm_scanner
import numpy as np
import math
import sys
import signal
import time
import logging

logger = logging.getLogger(__name__)

def scan_fm(fc):
    """
    Scan for FM stations with proper resource management
    
    Args:
        fc: Center frequency (single value, not np.arange)
    
    Returns:
        List of detected station frequencies
    """
    detected_stations = []
    tb = None
    
    try:
        tb = fm_scanner()
        fft_size = 2**7
        samp_rate = 2.048e6
        threshold = 0.3

        bin_bandwidth = samp_rate/fft_size
        fm_bandwidth = 200e3

        station_size = math.ceil(fm_bandwidth/bin_bandwidth)
        half_station_size = station_size/2 if station_size%2==0 else (station_size+1)/2

        logger.info(f"Starting FM scan at {fc/1e6:.1f} MHz")
        
        # Set frequency and start scanning
        tb.set_freq(fc)
        tb.start()
        tb.wait()
        
        # Get data
        data = tb.blocks_vector_sink_x_0.data()
        
        # Stop the flowgraph
        tb.stop()
        tb.wait()
        
        logger.info(f"Collected {len(data)} samples")
        
        if len(data) == 0:
            logger.warning("No data collected during scan")
            return detected_stations
        
        # Compute Candidate Frequencies
        step_size = 100e3
        start_freq = round_to_3_sigfigs(fc - samp_rate/2)
        end_freq = round_to_3_sigfigs(fc + samp_rate/2)
        candidate_freqs = np.arange(start_freq, end_freq, step_size)
        
        if len(candidate_freqs) < 3:
            logger.warning("Not enough candidate frequencies")
            return detected_stations
            
        candidate_freqs = candidate_freqs[1:-1]  # Avoid index error during summing power bins
        candidate_freqs_bin = np.round(((candidate_freqs - fc) * fft_size/samp_rate) + fft_size/2, 1).astype(int)

        power_per_station = np.zeros(candidate_freqs.size)

        # Process data in chunks
        for i in range(0, len(data), fft_size):
            if i + fft_size > len(data):
                break
                
            data_chunk = data[i:i+fft_size]
            
            for j, station_bin in enumerate(candidate_freqs_bin):
                start_bin = int(station_bin - half_station_size)
                end_bin = int(station_bin + half_station_size)
                
                # Ensure we don't go out of bounds
                start_bin = max(0, start_bin)
                end_bin = min(len(data_chunk), end_bin)
                
                if start_bin < end_bin:
                    potential_station = np.sum(np.abs(data_chunk[start_bin:end_bin])**2)
                    power_per_station[j] += potential_station

        if power_per_station.max() == power_per_station.min():
            logger.warning("No power variation detected")
            return detected_stations

        # Normalize power
        normalized_power_per_station = normalize(power_per_station)

        # Find active stations
        active_indices = np.where(normalized_power_per_station > threshold)[0]
        
        if len(active_indices) == 0:
            logger.info("No stations detected above threshold")
            return detected_stations

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
            detected_stations.append(candidate_freqs[max_idx])

        logger.info(f"Detected {len(detected_stations)} stations")
        
    except Exception as e:
        logger.error(f"Error during FM scan: {e}")
        
    finally:
        # Ensure proper cleanup
        if tb is not None:
            try:
                tb.stop()
                tb.wait()
                del tb
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    return detected_stations


def scan_fm_full_band(start_freq=88e6, end_freq=108e6, step_freq=2e6):
    """
    Scan the full FM band by stepping through frequencies
    
    Args:
        start_freq: Starting frequency (default 88 MHz)
        end_freq: Ending frequency (default 108 MHz) 
        step_freq: Step size (default 2 MHz)
    
    Returns:
        List of all detected station frequencies
    """
    all_stations = []
    
    # Generate center frequencies for scanning
    center_freqs = np.arange(start_freq + step_freq/2, end_freq, step_freq)
    
    for fc in center_freqs:
        logger.info(f"Scanning around {fc/1e6:.1f} MHz")
        stations = scan_fm(fc)
        all_stations.extend(stations)
        
        # Add delay between scans to ensure proper SDR cleanup
        time.sleep(1.0)
    
    # Remove duplicates and sort
    all_stations = list(set(all_stations))
    all_stations.sort()
    
    # Filter to actual FM band
    all_stations = [s for s in all_stations if start_freq <= s <= end_freq]
    
    logger.info(f"Total stations found: {len(all_stations)}")
    return all_stations


def normalize(x):
    """Normalize array to 0-1 range"""
    x_min, x_max = x.min(), x.max()
    if x_max == x_min:
        return np.zeros_like(x)
    return (x - x_min) / (x_max - x_min)


def round_to_3_sigfigs(x):
    """Round to 3 significant figures"""
    if x == 0:
        return 0
    else:
        return round(x, -int(math.floor(math.log10(abs(x))) - 2))