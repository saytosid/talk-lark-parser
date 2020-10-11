# Lark
A parsing toolkit for Python



# Overview
- Parsing  <!-- .element: class="fragment" data-fragment-index="1" -->
- Domain Specific Language  <!-- .element: class="fragment" data-fragment-index="2" -->



# Domain Specific Language
 - Communication with "Domain Experts"  <!-- .element: class="fragment" data-fragment-index="1" -->

Note: A custom language. Designed for domain-experts.  Convey their intent


## Why not use general-purpose languages?
 - Verbosity  <!-- .element: class="fragment" data-fragment-index="1" -->
 - Flexibility  <!-- .element: class="fragment" data-fragment-index="2" -->
 - Complexity  <!-- .element: class="fragment" data-fragment-index="3" -->

Note: General == Too verbose, more flexible (more bugs, edge case handling), too generic and often technical - SQL, JSON, etc.


## Advantages of DSL

1. Communication
  - Easy to understand  <!-- .element: class="fragment" data-fragment-index="1" -->
  - Meaningful errors  <!-- .element: class="fragment" data-fragment-index="2" -->
  - Less scope => Less errors  <!-- .element: class="fragment" data-fragment-index="3" -->
Note: eg: A commodities trader doesn't understand about data-structures or for-loops. But - product_class, delivery-specification, etc.  Easy communicate intent   Easy to interpret errors   Less scope so less errors


## Advantages of DSL

2. Validation
Note: Grammar only needs to be defined for specific use-cases. Can include domain specific validation within it's definition. Abstracting the input cleaning and edge case handling form app code.  App gets clean representations and does not need to include any business logic wrt parsing.


## Advantages of DSL

3. Reusability
Note: Grammars can be reused by applications and can be defined in one place. Eg: Regex is reused by many applications for string matching


## Some Use-cases
 - Rules to detect outliers in a Bond Pricing application
```sh [1-2|3]
if bond->price discounted using bond->benchmark_tenor
  moves more_than 5% than bond->previous_price
    then report "MARKET_THRESHOLD_BROKEN"
```


## Some Use-cases
 - Rules to infer data
```sh [1|2]
if ticker has port "Amsterdam"
  then ticker.location = "Netherland"
```



## Designing a language
 - Use popular idioms
 - Design for correctness

Note: Use well known domain specific keywords as opposed to technical software related terms.  Design for the use case and incorporate validation. Discourage abuse


## Writing a Grammar
 - [EBNF form](https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form#:~:text=In%20computer%20science%2C%20extended%20Backus,as%20a%20computer%20programming%20language.)
 
``` [1|2]
dict: "{" dict_item* "}"
dict_item: name ":" value
```
Note: EBNF is a grammar notation used to represent context-free grammars, FWIW we can use it to define a grammar as shown.



## Parsing with Lark
``` []
rule_name : list of rules and TERMINALS to match
          | another possible list of items
          | etc.

TERMINAL: "some text to match"
```


## Dict parser
``` [1|3-4|6|8-11|13-16]
dict: "{" [dict_item ("," dict_item)*] ","? "}"

dict_item: ESCAPED_STRING ":" value
    | SIGNED_NUMBER ":" value

list: "[" [value ("," value)*] ","? "]"

value: ESCAPED_STRING
    | SIGNED_NUMBER
    | dict
    | list

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.WS
%ignore WS
```


## Parsed tree
```python [1-5|7-10|12]
from pathlib import Path
from lark import Lark

grammar = Path(__file__).parent / "grammar.lark"
parser = Lark(grammar.read_text(), start="dict")

test_dict_1 = """
    {"one": 1, "two": 2}
    """
tree = parser.parse(test_dict_1)

print(tree.pretty())
```

``` [1|2,5|3,4,6,7]
dict
  dict_item
    "one"
    value       1
  dict_item
    "two"
    value       2
```

Note: Lark flattens terminals automatically, to force a flattening we can assign alias names to our nodes to make the tree a bit cleaner.


## Shaping the tree
```  [1-4|6-7]
value: ESCAPED_STRING  -> string
    | SIGNED_NUMBER     -> number
    | dict
    | list

string: ESCAPED_STRING
number: SIGNED_NUMBER
```

``` [1|2,5|3,4,6,7]
dict
  dict_item
    string      "one"
    number      1
  dict_item
    string      "two"
    number      2
```


## Tree Transformer

```python [1|2-3|5-6]
class DictTransformer(Transformer):
    def string(self, items):
        return str(items[0])

    def number(self, items):
        return int(items[0])
```

```python  [1-2| 4]
tree = parser.parse('{"one": 1, "two": 2}')
DictTransformer().transform(tree)

> {'"one"': 1, '"two"': 2}
```


## Tree Transformer
```python [8-9|11-13|15-16]
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
```


# Parsing Dict
```python [1-9|11]
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
```


``` [1|2-4|5-10|11-22]
dict
  dict_item
    string      "key_1"
    number      123
  dict_item
    string      "key_2"
    list
      number    1
      number    2
      number    3
  dict_item
    string      "key_3"
    dict
      dict_item
        number  1
        number  1
      dict_item
        number  2
        number  2
      dict_item
        number  3
        number  3
```


# Parsing Dict
```python [12]
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
```

```python [2|3|4]
{
    '"key_1"': 123,
    '"key_2"': [1, 2, 3],
    '"key_3"': {1: 1, 2: 2, 3: 3}
}
```

# References
 - https://tomassetti.me/domain-specific-languages/
 - https://github.com/lark-parser/lark