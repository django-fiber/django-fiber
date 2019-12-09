import re

import html.entities as html_entities


name2codepoint = html_entities.name2codepoint.copy()
name2codepoint['apos'] = ord("'")

_ENTITY_REF = re.compile(r'&(?:#(\d+)|(?:#x([\da-fA-F]+))|([a-zA-Z]+));')
_ENTITY_REPLACE = [
    lambda code: chr(int(code, 10)) if code else None,
    lambda code: chr(int(code, 16)) if code else None,
    lambda code: chr(name2codepoint[code]) if code in name2codepoint else None
]

def htmlentitydecode(s):
    def unescape(match):
        for i, sub in enumerate(_ENTITY_REPLACE, start=1):
            replaced = sub(match.group(i))
            if replaced is not None:
                return replaced
        return match.group(0)
    return _ENTITY_REF.sub(unescape, s)
