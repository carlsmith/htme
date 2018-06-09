# HTME: The Hypertext Markup Engine

*HTML for Python*

The Hypertext Markup Engine offers the most Pythonic way to express HTML,
with full support for inline SVG and MathML.

## Hello World

The following example creates a fully functional HTML5 document that uses the
W3Schools Unordered List example for its body:

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

HTME separates HTML generation into two concerns: 1) expressing nested trees
of elements and 2) generating HTML5 documents). It takes a different approach
to each of them:

1. Each type of element (DIV, SVG, IMG etc) is implemented as a custom class
   that you can instantiate directly or subclass and extend.

   Elements are just containers for state. They basically mashup a dictionary
   (of attributes) with a list (of child elements).

   Element classes have flexible constructor signatures that make it easy to
   initialize elements in a desired state.

   Element classes also implement a complete set of operators that complement
   the constructor signatures, accepting the same objects as operands as the
   constructors take as arguments. The operators make it easy to mutate the
   attributes and children of existing elements.

   Whenever an element is rendered, it simply uses HTML syntax to represent
   its current state.

2. HTME provides an engine that can create the HTML5 boilerplate for *any*
   document from about twenty simple attributes, which use common defaults,
   so you will normally only need to edit a handful of them.

   The engine automatically generates the doctype, the HTML, HEAD and BODY
   elements, every element inside the HEAD element, and all of the elements
   at the end of the BODY element (for loading CSS and JavaScript resources
   after the body is rendered). You only need to define the *tree* (the guts
   of the body) as a nested tree of elements.

   The engine also implements all of the operators that elements have for
   working with children, allowing you to operate on the tree directly.

   An instance of the engine is a container for state that uses HTML syntax
   to represent its current state (always a complete HTML5 document) when
   rendered.

## Promiscuity

The engine and elements can be used with other tools too. For exmaple, a
blog site may use the engine to generate its boilerplate, and then use a
Markdown parser to generate the guts of the body.

``` python
doc = Engine(title='My Cool Journal', favicon='/static/favicon.png')
with open('article.md') as file: doc *= markdown.render(file.read())
```

Elements *just work* with the `str.format` method, interactive interpreters
and anything else that serializes an object and does something useful with
the result.

## Project Status

The library is brand new, so we can not recommend using it in production yet.
However, it is well tested and has no known bugs.

Please see the wiki for more information, or open an issue to ask a question.

##  Installation

HTME is a single file that only depends on the Python Standard Library. You
can just copy the file into your project or library and you are good to go.

HTME will always be released as a single file without any third party deps,
so you can always upgrade it by just updating your copy of the file with a
newer version.

## Contributing

HTME is licensed under the GPL3, and contributions are very welcome.

We use doctests (which allow us to express what should happen as interactive
interpreter sessions in our docstrings). Doctests work well for this library
and make it easy for people to contribute.

The coding style is not PEP8 (but is readable and consistant). Please do not
worry about trying to copy it. Write your code your way.

## Code of Conduct

We do not feel any need for an explicit *Code of Conduct*, as we are pretty
old school in that respect. We aspire to a pure meritocracy, based on the
well established conventions of the free software community.

## Python 2 Support

HTME will provide exactly the same features whether the file is executed as
Python 2 or 3, at least as long as Python 2 is [officially maintained][1]
(till at least 2020).

[1]: https://legacy.python.org/dev/peps/pep-0373
