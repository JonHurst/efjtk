import json

from efjtk.convert import build_logbook, build_summary
from efj_parser import ValidationError
import efjtk.modify


_func_map = {
    "expand": efjtk.modify.expand_efj,
    "night": efjtk.modify.add_night_data,
    "vfr": efjtk.modify.add_vfr_flag,
    "fo": efjtk.modify.add_fo_role_flag,
    "ins": efjtk.modify.add_ins_flag,
    "logbook": build_logbook,
    "summary": build_summary,
}


def lambda_handler(event, context):
    data = json.loads(event["body"])
    in_ = data["efj"]
    action = data["action"]
    status = "failed"
    try:
        if action in _func_map:
            out = _func_map[action](in_)
            status = "success"
        else:
            out = "Not implemented"
    except ValidationError as ve:
        out = (f"efj_parser : {ve.line_number} : {ve.message}"
               f" : {ve.problem_string}")
    except Exception as e:
        out = str(e)
    return {
        'statusCode': 200,
        'body': json.dumps((out, status))
    }


if __name__ == "__main__":
    event = {
        "body": json.dumps({
            "efj": open("/home/jon/data/logbook").read(),
            "action": "summary",
            "config": ""
        })
    }
    print(lambda_handler(event, ""))
