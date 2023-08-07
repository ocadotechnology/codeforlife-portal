# TODO: Move to Address model once we create it
def sanitise_uk_postcode(postcode):
    if len(postcode) >= 5:  # Valid UK postcodes are at least 5 chars long
        outcode = postcode[:-3]  # UK incodes are always 3 characters

        # Insert a space between outcode and incode if there isn't already one
        if not outcode.endswith(" "):
            postcode = postcode[:-3] + " " + postcode[-3:]

    return postcode
