# About GNU Radio FM Receiver

## Project Overview

The **GNU Radio FM Receiver** is a modern, software-defined radio (SDR) application that provides comprehensive FM radio reception capabilities. Built using GNU Radio for signal processing and PyQt5 for the user interface, this project demonstrates how to build a simple or advance application using GNU Radio for backend.

## Project Goals

- **Educational**: Demonstrate practical use of GNU Radio as DSP backend
- **Functional**: Provide a fully-featured FM radio receiver
- **Modern**: Implement contemporary UI/UX design patterns
- **Extensible**: Create a foundation for advanced radio applications

##  Key Features

### Core Radio Functionality
- **FM Band Reception**: Full coverage of 88-108 MHz FM broadcast band
- **RDS Support**: Radio Data System decoding for station information
- **High-Quality Audio**: Professional-grade audio processing and output
- **Manual Tuning**: Precise frequency control with real-time feedback

### Station Management  
- **Automated Scanning**: Intelligent station discovery across the FM band
- **Station Memory**: Persistent storage of discovered stations
- **Quick Navigation**: One-click station switching and browsing

### Recording Capabilities
- **Audio Recording**: High-quality WAV file recording
- **Timestamped Files**: Automatic filename generation with date/time
- **Configurable Output**: User-selectable recording directory
- **Real-time Control**: Start/stop recording during playback

### Advanced Features
- **Debug Interface**: Comprehensive signal analysis tools
- **Spectrum Analysis**: Real-time frequency domain visualization
- **Waterfall Display**: Time-frequency signal visualization  
- **Constellation Plots**: Digital signal quality assessment
- **Filter Controls**: Adjustable RF gain and filtering parameters

## Technical Architecture

### Signal Processing Chain
```
SDR Hardware → GNU Radio Flowgraph → Audio Processing → PyQt5 UI
```

### Core Components

#### **GNU Radio Integration**
- Custom `rds_rx` flowgraph for FM demodulation
- Real-time signal processing and filtering
- RDS data extraction and decoding
- Audio output and recording pipeline

#### **PyQt5 User Interface**
- Modern, responsive design
- Tabbed interface for different application modes
- Custom widgets for radio-specific controls
- Real-time visualization integration

#### **Configuration Management**
- Persistent settings storage
- Station memory across sessions
- User preference management
- Automatic configuration backup

### Threading Architecture
- **Main Thread**: UI updates and user interaction
- **Scanner Thread**: Background frequency scanning
- **GNU Radio Thread**: Real-time signal processing

## Technology Stack

### **Core Technologies**
- **Python 3.8+**: Primary development language
- **GNU Radio 3.8+**: Signal processing framework
- **PyQt5**: Cross-platform GUI framework
- **NumPy**: Numerical computing support

### **Signal Processing**
- **Digital Signal Processing**: Real-time filtering and demodulation
- **RDS Decoding**: Radio Data System implementation
- **Audio Processing**: High-quality audio pipeline
- **Spectrum Analysis**: FFT-based frequency analysis

### **Hardware Support**
- **RTL-SDR**: USB dongle SDR support
- **HackRF**: Professional SDR hardware
- **USRP**: Universal Software Radio Peripheral
- **BladeRF**: High-performance SDR platform

## Contributing

This project is part of gsoc 2025 under GNU Radio organization, and contribution is welcomed 

### **Areas for Contribution**
- **Bug Reports**: Help identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Documentation**: Improve guides and examples
- **Testing**: Verify compatibility across platforms
- **UI/UX**: Enhance user interface design

## Project Status

### **Current Version**: 1.0.0
- ✅ Core FM reception functionality
- ✅ Station scanning and management
- ✅ Audio recording capabilities
- ✅ RDS data decoding
- ✅ Debug and analysis tools


##  License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

### **Special Thanks**
- **GNU Radio Community**: Especially my mentors for thier excellent guidance throughout the project period.

---
