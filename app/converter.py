import csv
import io
import uuid
from typing import Dict, List, Tuple


def parse_mapping(mapping: dict) -> List[Tuple[str, str]]:
    """
    Parses mapping JSON and returns list of (source_column, dwc_term)
    preserving order.
    """
    fields = mapping.get("fields", [])
    pairs: List[Tuple[str, str]] = []

    for field in fields:
        src = field.get("source_column")
        dst = field.get("dwc_term")
        if src and dst:
            pairs.append((src, dst))

    return pairs


def convert_csv_to_dwc(
    input_csv_bytes: bytes,
    mapping: dict,
    delimiter: str = ","
) -> bytes:
    """
    Convert input CSV bytes to Darwin Core CSV bytes using mapping.
    """
    mapping_pairs = parse_mapping(mapping)
    if not mapping_pairs:
        raise ValueError("Mapping has no fields.")

    input_text = input_csv_bytes.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(input_text), delimiter=delimiter)

    if not reader.fieldnames:
        raise ValueError("Input CSV has no header row.")

    output_headers = [dst for _, dst in mapping_pairs]

    output_io = io.StringIO()
    writer = csv.DictWriter(
        output_io,
        fieldnames=output_headers,
        delimiter=delimiter,
        extrasaction="ignore"
    )
    writer.writeheader()

    for row in reader:
        out_row: Dict[str, str] = {}

        for src, dst in mapping_pairs:
            out_row[dst] = row.get(src, "")

        # Ensure occurrenceID exists if part of mapping
        if "occurrenceID" in out_row and not out_row["occurrenceID"]:
            out_row["occurrenceID"] = str(uuid.uuid4())

        writer.writerow(out_row)

    return output_io.getvalue().encode("utf-8")
