# Image Requirements for SIH Report

## Required Images for main_clean.tex

The LaTeX document references the following image files that need to be added to the `images/` directory:

### Hardware Photos (JPG format, min 1920x1080)

1. **hardware_complete_model.jpg**
   - Complete MCB testing system overview
   - Show all major components integrated
   - Professional lighting, clear component visibility

2. **relay_matrix_board.jpg**
   - 6-channel relay control board
   - Close-up showing individual relays
   - Label key components (R1-R6)

3. **rl_impedance_bank.jpg**
   - R-L component bank with resistors and inductors
   - Show component values clearly
   - Highlight switching connections

4. **esp32_controller_setup.jpg**
   - ESP32 with voltage sensing circuits
   - WiFi antenna and connections visible
   - Show ADC connections and power supply

5. **mcb_test_station.jpg**
   - Universal MCB mounting slot
   - Safety interlocks and emergency stop
   - Arc containment enclosure

6. **software_hardware_integration.jpg**
   - Computer screen showing GUI + hardware
   - Live waveform display visible
   - Hardware status indicators active

7. **testing_validation_setup.jpg**
   - Complete test setup during demonstration
   - All components connected and operational
   - Professional testing environment

8. **waveform_demonstration.jpg**
   - Live waveform analysis on screen
   - Voltage and current traces visible
   - Phase difference clearly shown

9. **sih_presentation_setup.jpg**
   - Team presenting to judges
   - Hardware setup visible in background
   - Professional presentation environment

10. **judge_evaluation_moment.jpg**
    - Judges examining the hardware
    - Active demonstration in progress
    - Technical discussion captured

### Technical Diagrams (PNG format, high resolution)

1. **system_evolution_timeline.png**
   - Day 1, 2, 3 progression diagram
   - Show evolution from automation to AC control
   - Include key milestones and achievements

2. **rl_matrix_circuit_diagram.png**
   - Complete circuit schematic
   - All component values labeled
   - Relay switching paths highlighted
   - Professional circuit diagram style

## Image Directory Structure

```
images/
├── hardware_complete_model.jpg
├── relay_matrix_board.jpg
├── rl_impedance_bank.jpg
├── esp32_controller_setup.jpg
├── mcb_test_station.jpg
├── software_hardware_integration.jpg
├── testing_validation_setup.jpg
├── waveform_demonstration.jpg
├── sih_presentation_setup.jpg
├── judge_evaluation_moment.jpg
├── system_evolution_timeline.png
└── rl_matrix_circuit_diagram.png
```

## Image Guidelines

- **Resolution**: Minimum 1920x1080 for photos, 300 DPI for diagrams
- **Format**: JPG for photographs, PNG for technical diagrams
- **Quality**: High quality, professional appearance
- **Lighting**: Good lighting for hardware photos
- **Annotations**: Key components should be clearly visible
- **File Size**: Reasonable size for LaTeX compilation (< 5MB each)

## LaTeX Integration

The images are referenced using:
```latex
\includegraphics[width=0.8\textwidth]{images/filename.jpg}
```

Make sure all image files are placed in the `images/` directory relative to the main LaTeX file.

## Fallback Options

If actual photos are not available, you can:
1. Use placeholder images with proper dimensions
2. Create technical diagrams using drawing software
3. Use screenshots from the software interface
4. Generate circuit diagrams using circuit design tools

## Notes

- All images should maintain professional quality
- Ensure proper lighting and focus for hardware photos
- Technical diagrams should be clear and well-labeled
- Consider adding annotations or callouts for key features