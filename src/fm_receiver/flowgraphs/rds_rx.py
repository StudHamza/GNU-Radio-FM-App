#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Stereo FM receiver and RDS Decoder
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio.filter import firdes
import sip
from gnuradio import analog
import math
from gnuradio import audio
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio import fft
from gnuradio.fft import window
from gnuradio import gr
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import osmosdr
import time
import rds
import rds_rx_epy_block_0 as epy_block_0  # embedded python block



from gnuradio import qtgui

class rds_rx(gr.top_block, Qt.QWidget):

    def __init__(self, serial=23777405):
        gr.top_block.__init__(self, "Stereo FM receiver and RDS Decoder", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Stereo FM receiver and RDS Decoder")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "rds_rx")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Parameters
        ##################################################
        self.serial = serial

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 1920000
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(1.0, 19000,19000/8, 1.0, 151)
        self.freq_offset = freq_offset = 250e3
        self.freq = freq = 88.7
        self.volume = volume = -5
        self.tau_1 = tau_1 = 75e-6
        self.tau = tau = 75e-6
        self.rrc_taps_manchester = rrc_taps_manchester = [rrc_taps[n] - rrc_taps[n+8] for n in range(len(rrc_taps)-8)]
        self.pilot_taps = pilot_taps = firdes.complex_band_pass(1.0, 240000, 18980, 19020, 1000, window.WIN_HAMMING, 6.76)
        self.num_items = num_items = samp_rate*2
        self.mute = mute = 1
        self.mode = mode = 1
        self.gain = gain = 40
        self.freq_tune = freq_tune = freq*1e6-freq_offset
        self.fir_transition_width = fir_transition_width = 20e3
        self.fir_cutoff = fir_cutoff = 135e3
        self.fft_size = fft_size = 2**7
        self.done = done = 0
        self.decimation = decimation = 6

        ##################################################
        # Blocks
        ##################################################
        self._volume_range = Range(-20, 10, 1, -5, 200)
        self._volume_win = RangeWidget(self._volume_range, self.set_volume, "Volume", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._volume_win, 1, 0, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._gain_range = Range(0, 49.6, 1, 40, 200)
        self._gain_win = RangeWidget(self._gain_range, self.set_gain, "RF Gain", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._gain_win, 2, 0, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._freq_range = Range(77, 108, 0.1, 88.7, 200)
        self._freq_win = RangeWidget(self._freq_range, self.set_freq, "Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._freq_win, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._fir_transition_width_range = Range(10e3, 40e3, 1e3, 20e3, 200)
        self._fir_transition_width_win = RangeWidget(self._fir_transition_width_range, self.set_fir_transition_width, "Transition width", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._fir_transition_width_win)
        self._fir_cutoff_range = Range(20e3, 200e3, 1e3, 135e3, 200)
        self._fir_cutoff_win = RangeWidget(self._fir_cutoff_range, self.set_fir_cutoff, "Cutoff Frequency", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._fir_cutoff_win)
        self.rtlsdr_source_0_0 = osmosdr.source(
            args="numchan=" + str(1) + " " + f"rtl={serial}"
        )
        self.rtlsdr_source_0_0.set_time_unknown_pps(osmosdr.time_spec_t())
        self.rtlsdr_source_0_0.set_sample_rate(samp_rate)
        self.rtlsdr_source_0_0.set_center_freq(freq_tune, 0)
        self.rtlsdr_source_0_0.set_freq_corr(0, 0)
        self.rtlsdr_source_0_0.set_dc_offset_mode(0, 0)
        self.rtlsdr_source_0_0.set_iq_balance_mode(0, 0)
        self.rtlsdr_source_0_0.set_gain_mode(False, 0)
        self.rtlsdr_source_0_0.set_gain(gain, 0)
        self.rtlsdr_source_0_0.set_if_gain(20, 0)
        self.rtlsdr_source_0_0.set_bb_gain(20, 0)
        self.rtlsdr_source_0_0.set_antenna('', 0)
        self.rtlsdr_source_0_0.set_bandwidth(0, 0)
        self.rds_parser_0 = rds.parser(False, False, 0)
        self.rds_panel_0_0 = rds.rdsPanel(freq)
        self._rds_panel_0_0_win = self.rds_panel_0_0
        self.top_layout.addWidget(self._rds_panel_0_0_win)
        self.rds_panel_0 = rds.rdsPanel(freq)
        self._rds_panel_0_win = self.rds_panel_0
        self.top_grid_layout.addWidget(self._rds_panel_0_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rds_decoder_0 = rds.decoder(False, False)
        self.rational_resampler_xxx_1 = filter.rational_resampler_ccc(
                interpolation=19000,
                decimation=samp_rate // decimation // 10,
                taps=[],
                fractional_bw=0)
        self.rational_resampler_xxx_0 = filter.rational_resampler_fff(
                interpolation=240000,
                decimation=samp_rate // decimation,
                taps=[],
                fractional_bw=0)
        self.qtgui_waterfall_sink_x_0 = qtgui.waterfall_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate / decimation, #bw
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_waterfall_sink_x_0.set_update_time(0)
        self.qtgui_waterfall_sink_x_0.enable_grid(False)
        self.qtgui_waterfall_sink_x_0.enable_axis_labels(True)

        self.qtgui_waterfall_sink_x_0.disable_legend()

        self.qtgui_waterfall_sink_x_0.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
                  '', '', '', '', '']
        colors = [0, 0, 0, 0, 0,
                  0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
                  1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_waterfall_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_waterfall_sink_x_0.set_color_map(i, colors[i])
            self.qtgui_waterfall_sink_x_0.set_line_alpha(i, alphas[i])

        self.qtgui_waterfall_sink_x_0.set_intensity_range(-80, 0)

        self._qtgui_waterfall_sink_x_0_win = sip.wrapinstance(self.qtgui_waterfall_sink_x_0.qwidget(), Qt.QWidget)

        self.top_grid_layout.addWidget(self._qtgui_waterfall_sink_x_0_win, 5, 0, 1, 1)
        for r in range(5, 6):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_time_sink_x_0 = qtgui.time_sink_f(
            2**11, #size
            samp_rate, #samp_rate
            "", #name
            2, #number of inputs
            None # parent
        )
        self.qtgui_time_sink_x_0.set_update_time(0.05)
        self.qtgui_time_sink_x_0.set_y_axis(-0.5, 0.5)

        self.qtgui_time_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_time_sink_x_0.enable_tags(True)
        self.qtgui_time_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_time_sink_x_0.enable_autoscale(False)
        self.qtgui_time_sink_x_0.enable_grid(False)
        self.qtgui_time_sink_x_0.enable_axis_labels(True)
        self.qtgui_time_sink_x_0.enable_control_panel(False)
        self.qtgui_time_sink_x_0.enable_stem_plot(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'red', 'green', 'black', 'cyan',
            'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_time_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_time_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_time_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_time_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_time_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_time_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_time_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_time_sink_x_0_win = sip.wrapinstance(self.qtgui_time_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_time_sink_x_0_win)
        self.qtgui_freq_sink_x_1_0 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate / (decimation*5), #bw
            "L+R", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1_0.set_update_time(0)
        self.qtgui_freq_sink_x_1_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_1_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_1_0.enable_grid(False)
        self.qtgui_freq_sink_x_1_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_1_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_1_0.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_1_0.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_1_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_0_win)
        self.qtgui_freq_sink_x_1 = qtgui.freq_sink_f(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate / decimation, #bw
            "FM Demod", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_1.set_update_time(0)
        self.qtgui_freq_sink_x_1.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_1.enable_grid(False)
        self.qtgui_freq_sink_x_1.set_fft_average(0.1)
        self.qtgui_freq_sink_x_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_1.enable_control_panel(True)
        self.qtgui_freq_sink_x_1.set_fft_window_normalized(False)


        self.qtgui_freq_sink_x_1.set_plot_pos_half(not False)

        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_1.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_1_win)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            freq, #fc
            samp_rate / decimation, #bw
            "Base Band", #name
            1,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis(-140, 10)
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(True)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_win, 4, 0, 1, 1)
        for r in range(4, 5):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            1024, #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0)
        self.qtgui_const_sink_x_0.set_y_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_x_axis(-2, 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(False)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 6, 0, 1, 1)
        for r in range(6, 7):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.freq_xlating_fir_filter_xxx_1_0 = filter.freq_xlating_fir_filter_fcc(10, firdes.low_pass(1.0, samp_rate / decimation, 7.5e3, 5e3), 57e3, samp_rate / decimation)
        self.freq_xlating_fir_filter_xxx_0 = filter.freq_xlating_fir_filter_ccc(decimation, firdes.low_pass(1, samp_rate, fir_cutoff, fir_transition_width), freq_offset, samp_rate)
        self.fir_filter_xxx_2 = filter.fir_filter_ccc(1, rrc_taps_manchester)
        self.fir_filter_xxx_2.declare_sample_delay(0)
        self.fir_filter_xxx_1_0 = filter.fir_filter_fff(5, firdes.low_pass(-2.1,240000,15e3,2e3))
        self.fir_filter_xxx_1_0.declare_sample_delay(0)
        self.fir_filter_xxx_1 = filter.fir_filter_fff(5, firdes.low_pass(1.0,240000,15e3,2e3))
        self.fir_filter_xxx_1.declare_sample_delay(0)
        self.fir_filter_xxx_0 = filter.fir_filter_fcc(1, pilot_taps)
        self.fir_filter_xxx_0.declare_sample_delay(0)
        self.fft_vxx_0 = fft.fft_vcc(fft_size, True, window.blackmanharris(fft_size), True, 1)
        self.epy_block_0 = epy_block_0.blk(fft_size=fft_size, samp_rate=samp_rate, freq=freq*10**6, done=done)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_cc(
            digital.TED_ZERO_CROSSING,
            16,
            0.01,
            1.0,
            1.0,
            0.1,
            1,
            digital.constellation_bpsk().base(),
            digital.IR_MMSE_8TAP,
            128,
            [])
        self.digital_diff_decoder_bb_0 = digital.diff_decoder_bb(2, digital.DIFF_DIFFERENTIAL)
        self.digital_constellation_receiver_cb_0 = digital.constellation_receiver_cb(digital.constellation_bpsk().base(), 2*math.pi / 100, -0.002, 0.002)
        self.blocks_wavfile_sink_0 = blocks.wavfile_sink(
            'Output.wav',
            2,
            48000,
            blocks.FORMAT_WAV,
            blocks.FORMAT_FLOAT,
            False
            )
        self.blocks_vector_to_stream_0 = blocks.vector_to_stream(gr.sizeof_float*1, fft_size)
        self.blocks_sub_xx_0 = blocks.sub_ff(1)
        self.blocks_stream_to_vector_0 = blocks.stream_to_vector(gr.sizeof_gr_complex*1, fft_size)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_gr_complex*1,0,mode)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_multiply_xx_1 = blocks.multiply_vff(1)
        self.blocks_multiply_xx_0 = blocks.multiply_vcc(1)
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_ff(0 if mute else 10 ** (1. * volume / 10))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(0 if mute else 10 ** (1. * volume / 10))
        self.blocks_msgpair_to_var_0_0 = blocks.msg_pair_to_var(self.set_done)
        self.blocks_delay_0 = blocks.delay(gr.sizeof_float*1, (len(pilot_taps) - 1) // 2)
        self.blocks_complex_to_mag_squared_0 = blocks.complex_to_mag_squared(fft_size)
        self.blocks_complex_to_imag_0 = blocks.complex_to_imag(1)
        self.blocks_add_xx_0 = blocks.add_vff(1)
        self.audio_sink_0 = audio.sink(48000, '', True)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((samp_rate / decimation) / (2*math.pi*75000))
        self.analog_pll_refout_cc_0 = analog.pll_refout_cc(0.001, 2 * math.pi * 19020 / 240000, 2 * math.pi * 18980 / 240000)
        self.analog_fm_deemph_0_0_0 = analog.fm_deemph(fs=48000, tau=tau)
        self.analog_fm_deemph_0_0 = analog.fm_deemph(fs=48000, tau=tau)
        self.analog_agc_xx_0 = analog.agc_cc(2e-3, 0.585, 53)
        self.analog_agc_xx_0.set_max_gain(1000)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_0, 'done'), (self.blocks_msgpair_to_var_0_0, 'inpair'))
        self.msg_connect((self.rds_decoder_0, 'out'), (self.rds_parser_0, 'in'))
        self.msg_connect((self.rds_parser_0, 'out'), (self.rds_panel_0, 'in'))
        self.msg_connect((self.rds_parser_0, 'out'), (self.rds_panel_0_0, 'in'))
        self.connect((self.analog_agc_xx_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.analog_fm_deemph_0_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.analog_fm_deemph_0_0_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 0))
        self.connect((self.analog_pll_refout_cc_0, 0), (self.blocks_multiply_xx_0, 1))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.freq_xlating_fir_filter_xxx_1_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_freq_sink_x_1, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.qtgui_waterfall_sink_x_0, 0))
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.rational_resampler_xxx_0, 0))
        self.connect((self.blocks_add_xx_0, 0), (self.analog_fm_deemph_0_0_0, 0))
        self.connect((self.blocks_complex_to_imag_0, 0), (self.blocks_multiply_xx_1, 1))
        self.connect((self.blocks_complex_to_mag_squared_0, 0), (self.blocks_vector_to_stream_0, 0))
        self.connect((self.blocks_delay_0, 0), (self.blocks_multiply_xx_1, 0))
        self.connect((self.blocks_delay_0, 0), (self.fir_filter_xxx_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_wavfile_sink_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.qtgui_time_sink_x_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.audio_sink_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_wavfile_sink_0, 1))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.qtgui_time_sink_x_0, 0))
        self.connect((self.blocks_multiply_xx_0, 0), (self.blocks_complex_to_imag_0, 0))
        self.connect((self.blocks_multiply_xx_1, 0), (self.fir_filter_xxx_1_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.blocks_stream_to_vector_0, 0))
        self.connect((self.blocks_selector_0, 1), (self.freq_xlating_fir_filter_xxx_0, 0))
        self.connect((self.blocks_stream_to_vector_0, 0), (self.fft_vxx_0, 0))
        self.connect((self.blocks_sub_xx_0, 0), (self.analog_fm_deemph_0_0, 0))
        self.connect((self.blocks_vector_to_stream_0, 0), (self.epy_block_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 1), (self.blocks_null_sink_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 2), (self.blocks_null_sink_0, 1))
        self.connect((self.digital_constellation_receiver_cb_0, 3), (self.blocks_null_sink_0, 2))
        self.connect((self.digital_constellation_receiver_cb_0, 0), (self.digital_diff_decoder_bb_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0, 4), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_diff_decoder_bb_0, 0), (self.rds_decoder_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_constellation_receiver_cb_0, 0))
        self.connect((self.fft_vxx_0, 0), (self.blocks_complex_to_mag_squared_0, 0))
        self.connect((self.fir_filter_xxx_0, 0), (self.analog_pll_refout_cc_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.blocks_sub_xx_0, 0))
        self.connect((self.fir_filter_xxx_1, 0), (self.qtgui_freq_sink_x_1_0, 0))
        self.connect((self.fir_filter_xxx_1_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.fir_filter_xxx_1_0, 0), (self.blocks_sub_xx_0, 1))
        self.connect((self.fir_filter_xxx_2, 0), (self.analog_agc_xx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1_0, 0), (self.rational_resampler_xxx_1, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.blocks_delay_0, 0))
        self.connect((self.rational_resampler_xxx_0, 0), (self.fir_filter_xxx_0, 0))
        self.connect((self.rational_resampler_xxx_1, 0), (self.fir_filter_xxx_2, 0))
        self.connect((self.rtlsdr_source_0_0, 0), (self.blocks_selector_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rds_rx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_serial(self):
        return self.serial

    def set_serial(self, serial):
        self.serial = serial

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_num_items(self.samp_rate*2)
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate / self.decimation) / (2*math.pi*75000))
        self.epy_block_0.samp_rate = self.samp_rate
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fir_cutoff, self.fir_transition_width))
        self.freq_xlating_fir_filter_xxx_1_0.set_taps(firdes.low_pass(1.0, self.samp_rate / self.decimation, 7.5e3, 5e3))
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1_0.set_frequency_range(self.freq, self.samp_rate / (self.decimation*5))
        self.qtgui_time_sink_x_0.set_samp_rate(self.samp_rate)
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate / self.decimation)
        self.rtlsdr_source_0_0.set_sample_rate(self.samp_rate)

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps
        self.set_rrc_taps_manchester([self.rrc_taps[n] - self.rrc_taps[n+8] for n in range(len(self.rrc_taps)-8)])

    def get_freq_offset(self):
        return self.freq_offset

    def set_freq_offset(self, freq_offset):
        self.freq_offset = freq_offset
        self.set_freq_tune(self.freq*1e6-self.freq_offset)
        self.freq_xlating_fir_filter_xxx_0.set_center_freq(self.freq_offset)

    def get_freq(self):
        return self.freq

    def set_freq(self, freq):
        self.freq = freq
        self.set_freq_tune(self.freq*1e6-self.freq_offset)
        self.epy_block_0.freq = self.freq*10**6
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1_0.set_frequency_range(self.freq, self.samp_rate / (self.decimation*5))
        self.rds_panel_0.set_frequency(self.freq)
        self.rds_panel_0_0.set_frequency(self.freq)
        self.rds_parser_0.reset() # self.freq

    def get_volume(self):
        return self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.blocks_multiply_const_vxx_0.set_k(0 if self.mute else 10 ** (1. * self.volume / 10))
        self.blocks_multiply_const_vxx_0_0.set_k(0 if self.mute else 10 ** (1. * self.volume / 10))

    def get_tau_1(self):
        return self.tau_1

    def set_tau_1(self, tau_1):
        self.tau_1 = tau_1

    def get_tau(self):
        return self.tau

    def set_tau(self, tau):
        self.tau = tau

    def get_rrc_taps_manchester(self):
        return self.rrc_taps_manchester

    def set_rrc_taps_manchester(self, rrc_taps_manchester):
        self.rrc_taps_manchester = rrc_taps_manchester
        self.fir_filter_xxx_2.set_taps(self.rrc_taps_manchester)

    def get_pilot_taps(self):
        return self.pilot_taps

    def set_pilot_taps(self, pilot_taps):
        self.pilot_taps = pilot_taps
        self.blocks_delay_0.set_dly((len(self.pilot_taps) - 1) // 2)
        self.fir_filter_xxx_0.set_taps(self.pilot_taps)

    def get_num_items(self):
        return self.num_items

    def set_num_items(self, num_items):
        self.num_items = num_items

    def get_mute(self):
        return self.mute

    def set_mute(self, mute):
        self.mute = mute
        self.blocks_multiply_const_vxx_0.set_k(0 if self.mute else 10 ** (1. * self.volume / 10))
        self.blocks_multiply_const_vxx_0_0.set_k(0 if self.mute else 10 ** (1. * self.volume / 10))

    def get_mode(self):
        return self.mode

    def set_mode(self, mode):
        self.mode = mode
        self.blocks_selector_0.set_output_index(self.mode)

    def get_gain(self):
        return self.gain

    def set_gain(self, gain):
        self.gain = gain
        self.rtlsdr_source_0_0.set_gain(self.gain, 0)

    def get_freq_tune(self):
        return self.freq_tune

    def set_freq_tune(self, freq_tune):
        self.freq_tune = freq_tune
        self.rtlsdr_source_0_0.set_center_freq(self.freq_tune, 0)

    def get_fir_transition_width(self):
        return self.fir_transition_width

    def set_fir_transition_width(self, fir_transition_width):
        self.fir_transition_width = fir_transition_width
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fir_cutoff, self.fir_transition_width))

    def get_fir_cutoff(self):
        return self.fir_cutoff

    def set_fir_cutoff(self, fir_cutoff):
        self.fir_cutoff = fir_cutoff
        self.freq_xlating_fir_filter_xxx_0.set_taps(firdes.low_pass(1, self.samp_rate, self.fir_cutoff, self.fir_transition_width))

    def get_fft_size(self):
        return self.fft_size

    def set_fft_size(self, fft_size):
        self.fft_size = fft_size
        self.epy_block_0.fft_size = self.fft_size

    def get_done(self):
        return self.done

    def set_done(self, done):
        self.done = done
        self.epy_block_0.done = self.done

    def get_decimation(self):
        return self.decimation

    def set_decimation(self, decimation):
        self.decimation = decimation
        self.analog_quadrature_demod_cf_0.set_gain((self.samp_rate / self.decimation) / (2*math.pi*75000))
        self.freq_xlating_fir_filter_xxx_1_0.set_taps(firdes.low_pass(1.0, self.samp_rate / self.decimation, 7.5e3, 5e3))
        self.qtgui_freq_sink_x_0.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1.set_frequency_range(self.freq, self.samp_rate / self.decimation)
        self.qtgui_freq_sink_x_1_0.set_frequency_range(self.freq, self.samp_rate / (self.decimation*5))
        self.qtgui_waterfall_sink_x_0.set_frequency_range(0, self.samp_rate / self.decimation)



def argument_parser():
    parser = ArgumentParser()
    return parser


def main(top_block_cls=rds_rx, options=None):
    if options is None:
        options = argument_parser().parse_args()

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
