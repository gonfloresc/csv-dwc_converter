import csv
import io
from typing import Dict, List, Tuple, Optional
import uuid


def parse_mapping(mapping: dict) -> List[Tuple[str, str]]:
    """
    Mapping format (v0.1):
      {
        "fields": [
          {"source_column": "DateTime", "dwc_term": "eventDate"},
          ...
        ]
      }

    Returns a list of (source_column, dwc_term) preserving order.
    """
    fields = mapping.get("fields", [])
    pairs: List[Tuple[str, str]] = []

    for f in fields:
        src = f.get("source_column")
        dst = f.get("dwc_term")
        if src and dst:
            pairs.append((src, dst))

    return pairs


def _ensure_occurrence_id(row_out: Dict[str, str]) -> None:
    """
    If the output schema includes occurrenceID but it's empty,
    we generate one (v0.1) to avoid producing blank IDs.

    Note: This is a pragmatic choice for v0.1. Later we can replace it
    with a stable hash rule, or enforce an input ID.
    """
    if "occurrenceID" in row_out and (row_out["occurrenceID"] is None or str(row_out["occurrenceID"]).strip() == ""):
        row_out["occurrenceID"] = str(uuid.uuid4())


def convert_csv_to_dwc(
    input_csv_bytes: bytes,
    mapping: dict,
    delimiter: str = ",",
    ensure_occurrence_id: bool = True
) -> bytes:
    """
    Converts an input CSV to a Darwin Core CSV using a mapping.

    - input_csv_bytes: raw CSV bytes
    - mapping: dict describing mapping_default.json
    - delimiter: delimiter for reading/writing CSV (default comma)
    - ensure_occurrence_id: generate UUID if occurrenceID is present but empty
    mapping_pairs = parse_mapping(mapping)
    """
    if not mapping_pairs:
        raise ValueError("Mapping has no fields. Add at least 1 mapping field.")

    # Decode handling UTF-8 with possible BOM
    input_text = input_csv_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(input_text), delimiter=delimiter)

    if reader.fieldnames is None:
        raise ValueError("Input CSV appears to have no header row.")

    # Output headers are the dwc_terms, in mapping order
    out_headers = [dst for _, dst in mapping_pairs]

    out_io = io.StringIO()
    writer = csv.DictWriter(out_io, fieldnames=out_headers, delimiter=delimiter, extrasaction="ignore")
    writer.writeheader()

    for row in reader:
        out_row: Dict[str, str] = {}

        for src, dst in mapping_pairs:
            out_row[dst] = row.get(src, "")

        if ensure_occurrence_id:
            _ensure_occurrence_id(out_row)

        writer.writerow(out_row)

    return out_io.getvalue().encode("utf-8")
