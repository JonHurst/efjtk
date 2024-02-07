import json
import configparser as cp

from efj_convert.logbook import build_logbook, UnknownAircraftClass
from efj_convert.config import build_config
from efj_convert.expand import expand_efj
from efj_convert.night import add_night_data
from efj_convert.vfr import add_vfr_flag
from efj_convert.summary import build as build_summary


def logbook(in_, config):
    out = ""
    status = "failed"
    try:
        parser = cp.ConfigParser()
        parser.read_string(config)
        try:
            ac_classes = parser["aircraft.classes"]
        except KeyError:
            raise cp.Error
        out = build_logbook(in_, ac_classes)
        status = "success"
    except cp.Error:  # something fundametally wrong with ini file
        out = build_config(in_, "")
        status = "config"
    except UnknownAircraftClass:
        out = build_config(in_, config)
        status = "config"
    except Exception as e:
        out = str(e)
    return out, status


def lambda_handler(event, context):
    data = json.loads(event["body"])
    in_ = data["efj"]
    action = data["action"]
    status = "failed"
    try:
        if action == "logbook":
            out, status = logbook(in_, data["config"])
        elif action == "summary":
            out = build_summary(in_)
            status = "success"
        elif action == "expand":
            out = expand_efj(in_)
            status = "success"
        elif action == "night":
            out = add_night_data(in_)
            status = "success"
        elif action == "vfr":
            out = add_vfr_flag(in_)
            status = "success"
        else:
            out = "Not implemented"
    except Exception as e:
        out = str(e)
    return {
        'statusCode': 200,
        'body': json.dumps((out, status))
    }


if __name__ == "__main__":
    event = {
        "body": json.dumps({
            "efj": open("/home/jon/docs/logbook").read(),
            "action": "logbook",
            "config": ""
        })
    }
    print(lambda_handler(event, ""))
