from pydantic import BaseModel

class FetchRequest(BaseModel):
    mode: str
    req_type: str
    name: str = ""
    end_date: str = ""
    start_date: str = ""
    suffix: str = ""

def parse_filename(filename: str) -> FetchRequest:
    """
    Parse filename of the form:
    @mode@req_type@name[@end@start@suffix].html
    """
    stem = filename.rsplit(".", 1)[0]
    parts = stem.split("@")[1:]  # drop leading empty

    if len(parts) < 3:
        raise ValueError("Invalid filename format")

    mode, req_type, name = parts[0:3]
    end_date = parts[3] if len(parts) > 3 else ""
    start_date = parts[4] if len(parts) > 4 else ""
    suffix = parts[5] if len(parts) > 5 else ""

    return FetchRequest(
        mode=mode,
        req_type=req_type,
        name=name,
        end_date=end_date,
        start_date=start_date,
        suffix=suffix
    )
