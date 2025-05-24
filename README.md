# Visualisation in Data Science 

## Analyzing the football dataset
This repository is a data visualization project focused on football (soccer) analytics. It provides interactive and static visualizations to explore player and team performance metrics specifically for RCD Espanyol.

# Repository Structure 

```mermaid 
flowchart TB
    %% Data Layer
    subgraph "Data Layer"
        raw["Raw CSV Files"]:::data
        filtered["Filtered Player Info CSV"]:::data
        grouped["Grouped Players Data"]:::data
    end

    %% Processing & Visualization Layer
    subgraph "Processing & Visualization Layer"
        barviolin["bar_and_violin_plot.py"]:::process
        heatmap["heatmap.py"]:::process
        scatter["scatterplot.py"]:::process
        interactive["bar_and_violin_interactive.py"]:::process
        notebook["VDS2425_Football.ipynb"]:::process
    end

    %% Generated Figures
    subgraph "Generated Figures"
        figures["Figure Objects (JSON/Python)"]:::process
    end

    %% Web Application Layer
    subgraph "Web Application Layer"
        app["Flask App (app.py)"]:::web
        assets["Static Front-End Assets"]:::web
        readme["README.md"]:::meta
    end

    %% Client Layer
    client["Client Browser"]:::client

    %% Annotation
    perf("Precompute figures for performance"):::note

    %% Connections
    raw -->|"CSV"| barviolin
    raw -->|"CSV"| heatmap
    raw -->|"CSV"| scatter
    raw -->|"CSV"| interactive
    filtered -->|"CSV"| barviolin
    filtered -->|"CSV"| heatmap
    filtered -->|"CSV"| scatter
    filtered -->|"CSV"| interactive
    grouped -->|"CSV"| barviolin
    grouped -->|"CSV"| heatmap
    grouped -->|"CSV"| scatter
    grouped -->|"CSV"| interactive

    barviolin -->|"chart objects (JSON)"| figures
    heatmap -->|"chart objects (JSON)"| figures
    scatter -->|"chart objects (JSON)"| figures
    interactive -->|"interactive JSON"| figures

    figures -->|"load figures"| app
    assets -->|"serve assets"| app
    app -->|"HTTP"| client

    perf -.-> figures

    %% Click Events
    click raw "https://github.com/r-niemans/vds_visuals2425/tree/main/data/"
    click filtered "https://github.com/r-niemans/vds_visuals2425/blob/main/data/filtered_player_info.csv"
    click grouped "https://github.com/r-niemans/vds_visuals2425/tree/main/grouped_players/"
    click barviolin "https://github.com/r-niemans/vds_visuals2425/blob/main/bar_and_violin_plot.py"
    click heatmap "https://github.com/r-niemans/vds_visuals2425/blob/main/heatmap.py"
    click scatter "https://github.com/r-niemans/vds_visuals2425/blob/main/scatterplot.py"
    click interactive "https://github.com/r-niemans/vds_visuals2425/blob/main/bar_and_violin_interactive.py"
    click notebook "https://github.com/r-niemans/vds_visuals2425/blob/main/VDS2425_Football.ipynb"
    click figures "https://github.com/r-niemans/vds_visuals2425/tree/main/figures/"
    click app "https://github.com/r-niemans/vds_visuals2425/blob/main/app.py"
    click assets "https://github.com/r-niemans/vds_visuals2425/tree/main/assets/"
    click readme "https://github.com/r-niemans/vds_visuals2425/blob/main/README.md"

    %% Styles
    classDef data fill:#aed9e0,stroke:#333,stroke-width:1px
    classDef process fill:#c8e6c9,stroke:#333,stroke-width:1px
    classDef web fill:#ffcc80,stroke:#333,stroke-width:1px
    classDef client fill:#fff59d,stroke:#333,stroke-width:1px
    classDef meta fill:#eeeeee,stroke:#333,stroke-width:1px
    classDef note fill:#ffd54f,stroke:#333,stroke-width:1px,stroke-dasharray: 5 5

- `app.py` – Main application script (runs all the figures together in a web application).
- `bar_and_violin_plot.py` – Generates static bar and violin plots.
- `bar_and_violin_interactive.py` – Creates interactive versions of bar and violin plots.
- `scatterplot.py` – Produces scatter plot visualizations.
- `heatmap.py` – Generates heatmap visualizations.
- `VDS2425_Football.ipynb` – Main Jupyter Notebook for comprehensive analysis.
- `data/` – Contains raw and processed datasets.
- `figures/` – Stores generated figures and plots.
- `grouped_players/` – Includes data grouped by player positions and metrics.
- `assets/` – Contains images. 
- `VDS2425 Football.zip` – Compressed archive of the project files.
```

## Installation 
**Clone the repository:**
   ```bash
   git clone https://github.com/r-niemans/vds_visuals2425.git
   cd vds_visuals2425
```
## Usage
To run the application and therefore view and interact with all the visuals in one place:
```bash
python app.py
```

To run the visuals separately from one another: 
```bash
python bar_and_violin_plot.py
python bar_and_violin_interactive.py
python scatterplot.py
python heatmap.py
```
