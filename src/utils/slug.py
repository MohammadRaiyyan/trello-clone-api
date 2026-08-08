from slugify import slugify


def generate_slug(value: str) -> str:
    return slugify(
        value,
        max_length=100,
        word_boundary=True,
        lowercase=True,
    )
