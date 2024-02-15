from typing import Set

from efj_parser import Parser, ValidationError


def validate(in_: str) -> str:
    messages = []
    try:
        duties, sectors = Parser().parse(in_)
        messages.append(f"{len(sectors)} sectors")
        messages.append(f"{len(duties)} duties")
        unused_flags: Set[str] = set()
        for s in sectors:
            unused_flags = unused_flags.union(s.extra_flags)
        messages.append(f"Unused flags: {unused_flags}")
        return "\n".join(messages)
    except ValidationError as e:
        return str(e)
