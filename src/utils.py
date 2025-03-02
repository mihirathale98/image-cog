import re
import ast


def parse_json_response(response):
    try:
        matches = re.findall(r'```json(.*?)```', response, re.DOTALL)
        if matches:
            return ast.literal_eval(matches[0])
        else:
            return None
    except Exception as e:
        return None
    