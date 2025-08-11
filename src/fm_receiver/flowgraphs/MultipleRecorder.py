# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Multiple Recorder Block
# Author: hamza
# GNU Radio version: 3.10.1.1

from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal







class MultipleRecorder(gr.hier_block2):
    def __init__(self, fname='0', freq=0, freq_offset=0):
        gr.hier_block2.__init__(
            self, "Multiple Recorder Block",
                gr.io_signature(1, 1, gr.sizeof_gr_complex*1),
                gr.io_signature(0, 0, 0),
        )

        ##################################################
        # Parameters
        ##################################################
        self.fname = fname
        self.freq = freq
        self.freq_offset = freq_offset

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1920000
        self.freq_offset_250 = freq_offset_250 = freq_offset+250e3
        self.decimation = decimation = 4

        ##################################################
        # Blocks
        ##################################################
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=1,
                decimation=10,
                taps=[],
                fractional_bw=0)
        self.low_pass_filter_0 = filter.fir_filter_fff(
            1,
            firdes.low_pass(
                1,
                samp_rate,
                200e3,
                56e3,
                window.WIN_HAMMING,
                6.76))
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decimation, firdes.low_pass(1, samp_rate, 130e3, 70e3), freq_offset_250, samp_rate)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(
            fname,
            1,
            48000,
            blocks.FORMAT_WAV,
            blocks.FORMAT_PCM_16,
            False
            )
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate / decimation) / (2*math.pi*75000))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.low_pass_filter_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.low_pass_filter_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self, 0), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_wavfile_sink_0, 0))


    def get_fname(self):
        return self.fname

    def set_fname(self, fname):
        self.fname = fname
        self.blocks_wavfile_sink_0.open(self.fname)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.set_freq_offset_250(self.freq_offset+250e3)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate / self.decimation) / (2*math.pi*75000))
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1, self.samp_rate, 130e3, 70e3))
        self.low_pass_filter_0.set_taps(firdes.low_pass(1, self.samp_rate, 200e3, 56e3, window.WIN_HAMMING, 6.76))

    def get_freq_offset_250(self):
        return self.freq_offset_250

    def set_freq_offset_250(self, freq_offset_250):
        self.freq_offset_250 = freq_offset_250
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset_250)

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate / self.decimation) / (2*math.pi*75000))

