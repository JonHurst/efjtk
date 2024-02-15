import io
import efj_parser as ep
import configparser as cp


def build_config(in_: str, config: str) -> str:
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
    parser = cp.ConfigParser()
    parser.read_string(config)
    return parser["aircraft.classes"]
