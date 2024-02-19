import io
import efj_parser as ep
import configparser as cp


def build_config(in_: str, config: str) -> str:
    """Build a template for an INI file incorporating any unknown types

    :param in_: An eFJ file in string form
    :param config: An INI file in string form. This can be an empty string or
        can be the contents of an existing INI file to update.
    :return: An updated INI file in string form. Any non pre-existing types are
        added to the [aircraft.classes] section and assigned "spse" as a value.
    """
    _, sectors = ep.Parser().parse(in_)
    parser = cp.ConfigParser()
    parser.read_string(config)
    if "aircraft.classes" not in parser:
        parser["aircraft.classes"] = {}
    for s in sectors:
        if s.aircraft.type_ not in parser["aircraft.classes"]:
            parser["aircraft.classes"][s.aircraft.type_] = "spse"
    f = io.StringIO()
    parser.write(f)
    return f.getvalue()


def aircraft_classes(config: str) -> cp.SectionProxy:
    """Extract the [aircraft.classes] section from an INI string.

    :param config: An INI file in string form
    :return: A ConfigParser SectionProxy object. This can be treated as a non
        case-sensitive dict, with the aircraft type as key and its category as
        value.
    """
    parser = cp.ConfigParser()
    parser.read_string(config)
    return parser["aircraft.classes"]
