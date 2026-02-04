def format_sse_data(value: object) -> str:
    text = "" if value is None else str(value)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")
    return "".join(f"data: {line}\n" for line in lines) + "\n"