def to_tag(tag_string):
    # Override default taggit behavior of splitting input string.
    return [tag_string.upper()]