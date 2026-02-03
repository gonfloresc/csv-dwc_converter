import json
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import Response

from .converter import convert_csv_to_dwc

app = FastAPI(title="Darwin Core CSV Converter", version="0.1.0")


@app.get("/")
def root():
    return {"status": "ok", "version": app.version, "endpoints": ["/convert"]}


@app.post("/convert")
async def convert(
    csv_file: UploadFile = File(...),
    mapping_file: UploadFile = File(...),
):
    # Read CSV bytes
    csv_bytes = await csv_file.read()
    if not csv_bytes:
        raise HTTPException(status_code=400, detail="Empty CSV file.")

    # Read mapping JSON bytes
    mapping_bytes = await mapping_file.read()
    if not mapping_bytes:
        raise HTTPException(status_code=400, detail="Empty mapping JSON file.")

    try:
        mapping = json.loads(mapping_bytes.decode("utf-8"))
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid mapping JSON format.")

    try:
        out_bytes = convert_csv_to_dwc(csv_bytes, mapping)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return Response(
        content=out_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="dwc_output.csv"'},
    )
