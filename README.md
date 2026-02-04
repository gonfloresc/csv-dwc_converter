# csv-dwc_converter

Minimal converter for camera-trap records from a custom CSV format to Darwin Core – Occurrence.

Version: 0.1.0

---

## Overview

This prototype transforms CSV files with heterogeneous structures (typical of camera-trap projects)
into a format compatible with the Darwin Core (DwC) standard, using a configurable mapping file.

The goal of version v0.1 is to demonstrate a simple, modular, and replicable workflow:
CSV input → processing → Darwin Core CSV output.

---

## What it does

* Receives an input CSV file
* Receives a JSON mapping file (source column → Darwin Core term)
* Generates an output CSV compatible with Darwin Core – Occurrence

---

## What it does NOT do (v0.1)

* Does not validate scientific names
* Does not fully validate Darwin Core compliance
* Does not perform taxonomic control
* Does not validate data domains or types
* Does not include a graphical user interface

These features are intentionally left for future versions.

---

## Architecture

* Backend: FastAPI
* Processing: pandas
* Design: modular and decoupled (converter independent from the API layer)
* Optional deployment: Google Cloud Run
* Fully replicable locally without depending on Google Cloud

---

## Repository structure

```
csv-dwc_converter/
├── app/
│   ├── main.py              # FastAPI application
│   └── converter.py         # CSV → DwC conversion logic
│
├── mappings/
│   └── mapping_default.json # Source column → Darwin Core mapping
│
├── examples/
│   └── sample_input.csv     # Example CSV input
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Requirements

### Minimum environment

* Python 3.10 or newer
* pip
* Operating system: Linux, macOS, or Windows

### Optional

* Docker (for fully reproducible execution)
* Google Cloud SDK (`gcloud`) if deploying to Cloud Run

---

## Local execution (Python)

### 1. Clone the repository

```bash
git clone https://github.com/gonfloresc/csv-dwc_converter.git
cd csv-dwc_converter
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate the environment:

* Linux / macOS

```bash
source .venv/bin/activate
```

* Windows

```bash
.venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8080
```

### 5. Access the service

Open in a browser:

```
http://127.0.0.1:8080/
```

Expected response:

```json
{
  "status": "ok",
  "version": "0.1.0",
  "endpoints": ["/convert"]
}
```

---

## Example usage: CSV → Darwin Core conversion

### 1. Run the conversion

```bash
curl -X POST http://127.0.0.1:8080/convert \\
  -F "csv_file=@examples/sample_input.csv" \\
  -F "mapping_file=@mappings/mapping_default.json" \\
  --output dwc_output.csv
```

### 2. Check the output file

```bash
head -n 5 dwc_output.csv
```

Expected header:

```text
occurrenceID,locationID,eventDate,scientificName,individualCount
```

---

## Local execution with Docker (optional)

### 1. Build the image

```bash
docker build -t csv-dwc-converter:0.1 .
```

### 2. Run the container

```bash
docker run --rm -p 8080:8080 csv-dwc-converter:0.1
```

The API will be available at:

```
http://127.0.0.1:8080/
```

---

## Deployment to Google Cloud Run (optional)

> ⚠️ Requires a Google Cloud account with Billing enabled.
> The service can be deployed with minimal cost configuration, and resources can be removed after a demo.

### 1. Enable required services

```bash
gcloud services enable \\
  run.googleapis.com \\
  cloudbuild.googleapis.com \\
  artifactregistry.googleapis.com
```

### 2. Deploy the service

```bash
gcloud run deploy csv-dwc-converter \\
  --source . \\
  --region us-central1 \\
  --platform managed \\
  --min-instances 0 \\
  --max-instances 1
```

Applied configuration:

* Scales to zero when idle
* Maximum of one instance
* Suitable for prototypes and demos

---

## Cost control (Google Cloud)

To keep costs close to zero:

* Use `min-instances = 0`
* Keep the service private when not in use
* Delete the Cloud Run service after demos
* Delete images from Artifact Registry if they are not needed

Example cleanup:

```bash
gcloud run services delete csv-dwc-converter --region us-central1
```

---

## Versioning

* **v0.1.0**

  * Basic CSV → Darwin Core (Occurrence) conversion
  * Explicit mapping via JSON file
  * No semantic or taxonomic validation

---

## Roadmap / Future versions

* Darwin Core field validation
* Taxonomic verification and normalization
* Error and warning reports
* Simple web interface
* Support for additional Darwin Core classes (Event, Location, MeasurementOrFact)

---

## License

MIT License. See LICENSE.

