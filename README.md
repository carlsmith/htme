# The Hypertext Markup Engine

HTME is a simple, Pythonic library for creating and maintaining HTML5
documents, with inline SVG and MathML support built in.

## Hello World

The following example creates a complete, fully functional HTML5 page,
with the W3Schools Unordered List example as its body:

``` python
doc = Engine(title='HTME', favicon='/static/favicon.png')
doc *= UL(LI(item) for item in ('Coffee', 'Tea', 'Milk'))
```

Printing `doc` would then output this code (the real output would not
contain insignificant whitespace):

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

## How HTME Works

HTME elements have flexible signatures and powerful operators that make it
easy to create and mutate DOM trees in a domain specific dialect of Python
2 or 3.

HTME also provides an engine that is able to generate HTML5 documents from
a set of simple attributes, only requiring users to define the guts of the
body as a tree of elements.

You can use the elements without the engine, or use the engine without the
elements. They just happen to work really well together too.

## Project Status

The library is brand new, but it is well tested and has no known bugs. The
license is GPL3. Contributions are welcome. Please see the wiki for more
information or open an issue to ask any questions.
