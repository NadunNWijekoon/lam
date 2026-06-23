# LAM - Real-Time Simulation Platform

**"Simulate Reality in Real Time"**

LAM is a sophisticated real-time traffic simulation and analysis platform that combines AI-powered prediction, weather modeling, and interactive visualization. Built with Python and PySide6, it provides a comprehensive environment for simulating complex urban traffic systems and generating detailed analytical reports.

---

## Features

- **🚗 Real-Time Traffic Engine**: Continuous traffic simulation with dynamic vehicle movement and intersection management
- **🌦️ Weather Simulation**: Integrated weather management system affecting traffic behavior and conditions
- **🤖 AI Prediction**: Machine learning-based traffic forecasting and prediction
- **📊 Analytics Dashboard**: Real-time visualization of traffic metrics and system statistics
- **📈 Report Generation**: Export simulation data as comprehensive reports in multiple formats (PDF, Excel)
- **🗺️ Network Modeling**: Graph-based city infrastructure representation using NetworkX
- **💾 Data Persistence**: SQLite database for storing simulation history and configuration
- **🎨 Modern UI**: Clean, intuitive interface with multiple view tabs
- **⚙️ Configurable Simulations**: Customizable simulation parameters and settings

---

## Project Structure

```
lam/
├── main.py                      # Application entry point
├── config.py                    # Configuration and styling settings
├── requirements.txt             # Python dependencies
│
├── database/                    # Database management
│   ├── __init__.py
│   └── db_manager.py           # SQLite database operations
│
├── models/                      # Data models
│   ├── __init__.py
│   ├── vehicle.py              # Vehicle entity model
│   └── event.py                # Event/incident model
│
├── services/                    # Business logic services
│   ├── __init__.py
│   └── report_generator.py      # Report generation service
│
├── simulations/                 # Simulation engines
│   ├── __init__.py
│   ├── ai/                      # AI/ML prediction
│   │   ├── __init__.py
│   │   └── predictor.py
│   ├── traffic/                 # Traffic simulation
│   │   ├── __init__.py
│   │   └── traffic_engine.py
│   └── weather/                 # Weather simulation
│       ├── __init__.py
│       └── weather_manager.py
│
├── ui/                          # User interface
│   ├── __init__.py
│   ├── main_window.py           # Main application window
│   ├── settings_tab.py          # Settings interface
│   ├── simulation_view.py       # Simulation visualization
│   ├── simulations_tab.py       # Simulations management
│   ├── analytics/               # Analytics visualization
│   │   ├── __init__.py
│   │   └── analytics_tab.py
│   ├── dashboard/               # Dashboard display
│   │   ├── __init__.py
│   │   └── dashboard_tab.py
│   └── reports/                 # Reports interface
│       ├── __init__.py
│       └── reports_tab.py
│
├── assets/                      # Application resources
│   ├── generate_assets.py       # Asset generation utility
│   └── icons/                   # Application icons
│
├── tests/                       # Test suite
│   └── test_simulation.py
│
└── exports/                     # Generated reports and exports (auto-created)
```

---

## Technologies Used

- **Python 3.7+** - Core language
- **PySide6** - GUI framework (Qt6 Python bindings)
- **NumPy** - Numerical computing
- **Pandas** - Data manipulation and analysis
- **Matplotlib** - Data visualization
- **NetworkX** - Network/graph analysis
- **scikit-learn** - Machine learning
- **ReportLab** - PDF generation
- **openpyxl** - Excel file handling
- **FastAPI** - (Optional) API framework
- **SQLite** - Database

---

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd lam
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the Application

### Start LAM

```bash
python main.py
```

This will launch the main application window with the traffic simulation interface.

### Available Tabs

1. **Dashboard** - Overview of real-time traffic metrics
2. **Simulations** - Manage and control simulation scenarios
3. **Analytics** - Detailed traffic analysis and statistics
4. **Reports** - Generate and export simulation reports
5. **Settings** - Configure application preferences

---

## Configuration

Edit `config.py` to customize:

- **Application Settings**: App name, display settings
- **Path Configuration**: Database location, export directory, assets directory
- **Theme Colors**: UI color scheme (primary, secondary, danger, etc.)
- **Simulation Parameters**: Grid dimensions, vehicle limits, weather impact factors

Key configuration options:

```python
APP_NAME = "LAM"                    # Application name
TAGLINE = "Simulate Reality in Real Time"
DATABASE_PATH = "database/simulation.db"
COLOR_PRIMARY = "#1565C0"           # Primary UI color
GRID_ROWS = 20                      # Simulation grid rows
GRID_COLS = 20                      # Simulation grid columns
MAX_VEHICLES = 500                  # Maximum vehicles in simulation
WEATHER_IMPACT = 0.3                # Weather effect on traffic (0-1)
```

---

## Core Components

### Traffic Engine (`simulations/traffic/traffic_engine.py`)

- Runs as a background thread
- Manages vehicle movement and intersection logic
- Emits tick signals for UI updates
- Integrates weather and AI prediction systems

### Database Manager (`database/db_manager.py`)

- Handles SQLite database operations
- Stores vehicle data, events, and simulation history
- Provides query interfaces for analysis

### Weather Manager (`simulations/weather/weather_manager.py`)

- Simulates dynamic weather conditions
- Impacts traffic behavior and visibility
- Generates weather events

### AI Predictor (`simulations/ai/predictor.py`)

- Uses scikit-learn for traffic prediction
- Forecasts congestion and bottlenecks
- Provides recommendations

### Report Generator (`services/report_generator.py`)

- Exports simulation data to PDF and Excel
- Generates statistical summaries
- Creates visualizations for reports

---

## Usage Examples

### Running a Custom Simulation

1. Launch the application
2. Go to the **Simulations** tab
3. Configure simulation parameters
4. Click "Start Simulation"
5. Monitor progress in the **Dashboard** tab

### Generating Reports

1. After running a simulation, go to the **Reports** tab
2. Select the simulation to report on
3. Choose export format (PDF or Excel)
4. Click "Generate Report"
5. File will be saved to the `exports/` directory

### Viewing Analytics

1. Open the **Analytics** tab
2. Select time range and metrics
3. View real-time charts and statistics

---

## Database

LAM uses SQLite for persistent storage. The database file is created automatically at:

```
database/simulation.db
```

### Key Tables

- `vehicles` - Vehicle entities and state
- `events` - Incidents and simulation events
- `simulations` - Simulation run history
- `weather_data` - Weather snapshots
- `predictions` - AI model predictions

---

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Building Assets

```bash
python assets/generate_assets.py
```

### Code Structure Guidelines

- Each module should have clear responsibilities
- UI components in `ui/` directory
- Simulation logic in `simulations/` directory
- Models in `models/` directory
- Reusable services in `services/` directory

---

## Troubleshooting

### Application won't start

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (must be 3.7+)
- Verify `config.py` has correct paths

### Database errors

- Delete `database/simulation.db` and restart (will recreate empty database)
- Check file permissions in `database/` directory

### UI rendering issues

- Update PySide6: `pip install --upgrade PySide6`
- Verify graphics drivers are up-to-date
- Try changing theme in Settings tab

### Simulation not running

- Check that traffic engine thread has started
- Monitor console for error messages
- Verify vehicle and grid configuration in `config.py`

---

## Performance Notes

- Optimal performance: 300-500 vehicles with 20x20 grid
- Increase `MAX_VEHICLES` for larger simulations (may impact responsiveness)
- Weather and AI features can be toggled for performance tuning
- Database queries may slow down with large historical data (consider archiving old data)

---

## Contributing

To contribute to LAM:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes following the code structure guidelines
3. Test thoroughly: `pytest tests/`
4. Submit a pull request with a clear description

---

## License

Specify your license here (e.g., MIT, GPL, etc.)

---

## Support

For issues, feature requests, or questions:

- Check existing documentation and FAQs
- Review console output for error messages
- Consult configuration options in `config.py`

---

## Version History

- **v1.0.0** - Initial release
  - Core traffic simulation engine
  - Real-time dashboard and analytics
  - Report generation
  - Weather simulation
  - AI prediction integration

---

## Acknowledgments

Built with Python, PySide6, and the open-source community.
