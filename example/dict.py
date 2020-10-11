from pathlib import Path
from typing import Dict

from lark import Lark, Transformer

grammar = Path(__file__).parent / "grammar.lark"
parser = Lark(grammar.read_text(), start="dict")

test_dict_1 = """
    {"one": 1, "two": 2}
    """
tree = parser.parse(test_dict_1)

print(tree.pretty())


class DictTransformer(Transformer):
    def string(self, items):
        return str(items[0])

    def number(self, items):
        return int(items[0])

    def list(self, items):
        return list(items)

    def dict_item(self, key_value):
        k, v = key_value
        return k, v

    def dict(self, items):
        return dict(items)


transformer = DictTransformer()
parsed_object = transformer.transform(tree)

print(parsed_object)

tree = parser.parse(
    """
    {
        "key_1": 123,
        "key_2": [1, 2, 3,],
        "key_3": {1:1, 2:2, 3:3},
    }
    """
)

print(tree.pretty())
print(transformer.transform(tree))
