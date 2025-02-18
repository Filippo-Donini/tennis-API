# Tennis Stats Explorer

A web application built with FastAPI that provides tennis statistics, head-to-head player comparisons, and live ATP/WTA rankings.

## Features

- **Head-to-Head Comparison**: Compare match histories between any two players from the same tour (ATP or WTA).
- **Live Rankings**: View current ATP and WTA rankings updated daily.
- **Comprehensive Statistics**: Access detailed match statistics and historical data.

## Deployment

The application is deployed on AWS EC2 and can be accessed at:
http://44.201.186.157:8000


## Project Structure

- tennis-stats/
├── main.py              # FastAPI application entry point
├── models.py            # SQLAlchemy models
├── database.py          # Database configuration
├── fetching_script.py   # Rankings update script
├── requirements.txt     # Python dependencies
├── Dockerfile          
├── routers/
│   ├── players.py      # Player-related routes
│   └── rankings.py     # Rankings-related routes
└── templates/          # Jinja2 HTML templates
    ├── base.html
    ├── home.html
    ├── rankings.html
    └── head_to_head.html
