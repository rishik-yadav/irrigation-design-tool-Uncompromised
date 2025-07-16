irrigation_design_tool/
├── app.py
├── requirements.txt
├── utils/
│   ├── __init__.py
│   ├── calculations.py
│   └── updated_cal.py
├── static/
│   ├── css/
│   │   ├── style.css        
│   │   └── stylehome.css     
│   ├── js/
│   │   └── map.js             
│   └── images/
│       ├── logo.png
│       └── irrigation.png
└── templates/
    ├── base.html              ← HTML base layout (navbar, head, etc.)
    ├── index.html             ← Home page
    ├── manual.html            ← Area/elevation manual input
    ├── boundary.html          ← Map-based input with Leaflet
    ├── inputs.html            ← Crop/system info form
    ├── results.html           ← With "Suggest" zones
    ├── results1.html          ← For manual zone entry
    ├── inventory.html         ← User can customize components
    └── final-summary.html     ← Summary + PDF download
