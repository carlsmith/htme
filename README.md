# HTME: The Hypertext Markup Engine

The Hypertext Markup Engine (HTME) aims to replace templating languages (like
Jinja 2) and crude DSLs (like Stan) with a Pythonic way to express HTML trees
and documents (with inline SVG and MathML support).

## Hello World

The following example creates a complete, fully functional HTML5 page, with
the W3Schools Unordered List example as its body:

``` python
doc = Engine(title='HTME', favicon='/static/favicon.png')
doc *= UL(LI(item) for item in ('Coffee', 'Tea', 'Milk'))
```

Printing `doc` would then output this code (the real output would not contain
insignificant whitespace):

``` html
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta content="ie=edge" http-equiv="x-ua-compatible">
    <title>HTME</title>
    <meta content="width=device-width, initial-scale=1" name="viewport">
    <link href="/static/favicon.png" rel="icon">
</head>
<body>
    <ul>
        <li>Coffee</li>
        <li>Tea</li>
        <li>Milk</li>
    </ul>
</body>
</html>
```

## Quick Explanation

HTME elements have flexible signatures and powerful operators that make it
easy to create and mutate DOM trees in a domain specific dialect of Python
2 or 3.

HTME also provides an engine that is able to generate HTML5 documents from
a set of simple attributes, only requiring users to define the guts of the
body as a tree of elements.

## Project Status

The library is brand new, but it is well tested and has no known bugs. The
license is GPL3. Contributions are welcome. Please see the wiki for more
information or open an issue to ask any questions.

##  Installation

HTME is a single file that only depends on the Python Standard Library. You
can just copy the file into your project or library and you are good to go.

HTME will always be released as a single file without any third party deps,
so you can always upgrade it by just updating your copy of the file with a
newer version.

## Python 2 and 3

HTME will provide exactly the same features whether the file is executed as
Python 2 or 3 for at least as long as Python 2 is [officially maintained][1].

[1]: https://legacy.python.org/dev/peps/pep-0373
