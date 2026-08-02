def get_avatar_text(full_name: str | None) -> str:
    if not full_name or not full_name.strip():
        return "?"

    words = full_name.strip().split()

    if len(words) == 1:
        return words[0][:2].upper()

    first = words[0][0]
    last = words[-1][0]

    return (first + last).upper()
