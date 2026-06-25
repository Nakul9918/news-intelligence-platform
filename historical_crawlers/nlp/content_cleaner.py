import re


# =====================================================
# Clean Article Content
# =====================================================

REMOVE_LINES = [

    "Live Events",

    "Advertisement",

    "Ads",

    "Read More",

    "Follow us",

    "Subscribe",

    "Join us",

    "Click here"

]


def clean_content(content):

    if not content:
        return ""

    # ---------------------------------------------
    # Remove extra spaces
    # ---------------------------------------------

    content = re.sub(
        r"\s+",
        " ",
        content
    )

    # ---------------------------------------------
    # Split into lines
    # ---------------------------------------------

    lines = content.split(".")

    cleaned_lines = []

    seen = set()

    for line in lines:

        line = line.strip()

        if len(line) < 15:
            continue

        skip = False

        for word in REMOVE_LINES:

            if word.lower() in line.lower():

                skip = True

                break

        if skip:
            continue

        if line in seen:
            continue

        seen.add(line)

        cleaned_lines.append(line)

    cleaned_text = ". ".join(cleaned_lines)

    return cleaned_text.strip()