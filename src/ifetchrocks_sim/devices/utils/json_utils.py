from json import JSONDecoder
from collections import OrderedDict

def json_ordered_dump(data: str) -> OrderedDict:
    customdecoder = JSONDecoder(object_pairs_hook=OrderedDict)
    return customdecoder.decode(data)