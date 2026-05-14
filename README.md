# Silverleaf Ops Insight Tool

Ops Insight is an AI-powered fee collection analytics dashboard built for Silverleaf Academy's scaling journey in Tanzania.

## Quick Start

### Using Docker (Recommended)

```bash
# Build and run
docker-compose up --build

# Open http://localhost:8501 in your browser
```

### Local Development

```bash
# Setup Python env
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run Streamlit app
streamlit run streamlit_app.py
```

Then open http://localhost:8501

### Live Production

Visit the link below to access the live dashboard

https://silverleaf-ops-insight.onrender.com

## Features

- **Fee Collection Analytics**: Track collection rates by campus
- **Outstanding Balance Tracking**: Identify overdue payments
- **AI-Powered Anomaly Detection**: Flag unusual fee patterns (erroneous entries, long-term outstanding)
- **Dashboard**: Real-time visualization of fee data
- **CSV Upload**: Upload monthly fee records for instant analysis

## Use Case

Silverleaf currently manages 1,200 students across 5 campuses in Arusha, Tanzania. Fee collection is manual and fragmented across Excel sheets. As we scale to 30 schools, this tool provides:

1. **Visibility**: Single view of collection health across all campuses
2. **Efficiency**: Automated anomaly detection flags problems early
3. **Scalability**: Data-driven insights without proportional headcount growth
4. **Context**: Built for Tanzanian reality (TZS, offline-first design, low-bandwidth friendly)

## Architecture

```
Streamlit UI
        ↓
Data Processor (pandas) + Anomaly Detector (sklearn Isolation Forest)
        ↓
CSV Analysis & Reporting
```

## Sample Data

Pre-loaded with ~800 realistic student fee records across 5 campuses:
- **Boma, Kijenge, Usa River, Ilboru, Sakina**
- Base fee: 600,000 TZS (~$260/month)
- Payment patterns: 65% paid, 20% partial, 15% outstanding
- Anomalies: 5% flagged entries (high fees, very old outstanding)

Click "Load Sample Data" to see it in action.

## Deployment Notes

### For Tanzania Context
- **Offline-first CSV**: No dependency on APIs; works with downloaded files
- **Mobile-friendly dashboard**: 5 campuses, 30+ soon; responsive design
- **Low bandwidth**: No video embeds, minimal external libs, gzip-friendly
- **Cost**: TZS-native currency display; cost-per-student metrics in roadmap

### Production Deployment

```bash
# Docker Hub
docker build -t silverleaf/ops-insight .
docker push silverleaf/ops-insight

# AWS/GCP/Azure
docker run -p 5000:5000 silverleaf/ops-insight

# Or use docker-compose on VPS
docker-compose up -d
```