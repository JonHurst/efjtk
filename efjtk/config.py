import io
import efj_parser as ep
import configparser as cp


def _parse_config(config: str) -> cp.ConfigParser:
    """Create a clean ConfigParser from a string

    :param config: The contents of an INI file as a string
    :return: A ConfigParser that is guaranteed to have an aircraft.classes
        section, with the entries within guaranteed to have a valid value.
    :raises configparser.Error: Any configparser exception when parsing the
        string is not caught, so must be handled at a higher level
    """
    parser = cp.ConfigParser()
    parser.read_string(config)  # raises cp.Error on failure
    if "aircraft.classes" not in parser:
        parser.add_section("aircraft.classes")
    for name, value in parser.items("aircraft.classes"):
        if value not in {"spse", "spme", "mc"}:
            parser.remove_option("aircraft.classes", name)
    return parser


def build_config(in_: str, config: str, raise_on_error: bool = False) -> str:
    """Build a template for an INI file incorporating any unknown types

    :param in_: An eFJ file in string form
    :param config: An INI file in string form. This can be an empty string or
        can be the contents of an existing INI file to update.
    :param raise_on_error: If an exception occurs while parsing the config
        string, reraise it rather than continuing with empty parser
    :return: An updated INI file in string form. Any non pre-existing types are
        added to the [aircraft.classes] section and assigned "spse" as a value.
    :raises configparser.Error: Any configparser exception caused by errors in
        config must be handled at higher level if raise_on_error is True
    """
    _, sectors = ep.Parser().parse(in_)
    try:
        parser = _parse_config(config)
    except cp.Error as e:
        if raise_on_error:
            raise e
        parser = cp.ConfigParser()
        parser.add_section("aircraft.classes")
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
        value. Uses empty parser if parsing of config fails.
    """
    try:
        parser = _parse_config(config)
    except cp.Error:
        parser = cp.ConfigParser()
        parser.add_section("aircraft_classes")
    return parser["aircraft.classes"]
