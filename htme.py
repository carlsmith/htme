"""
                HTME | The Hypertext Markup Engine
                ==================================                          """

from __future__ import print_function, unicode_literals
from types import GeneratorType

# The ASCII global constants...

empty, tab, newline, space, underscore, quote = "", "\t", "\n", " ", "_", "'"
bar, colon, bang, ask, pound, dollar = "|", ":", "!", "?", "#", "$"
dot, comma, plus, minus, ampersand, at = ".", ",", "+", "-", "&", "@"
modulo, caret, asterisk, equals, semicolon = "%", "^", "*", "=", ";"
slash, backslash, backtick, tilde, doublequote = "/", "\\", "`", "~", '"'
openparen, closedparen, openbracket, closedbracket = "(", ")", "[", "]"
openbrace, closedbrace, openangle, closedangle = "{", "}", "<", ">"

# The generic helper functions...

def read(path): # TODO: look into `io.open` for unicode (bipy) support

    """This simple helper function wraps `file.read` with the idiomatic
    with-statement, so we can read from a file in a single expression.
    It takes one required arg (`path`) which is a path to the file,
    and returns the body of the file as a string."""

    with open(path, "r") as file: return file.read()

def readlines(path):

    """This helper function works just like `read`, but returns the file
    as a list of lines (instead of a string)."""

    with open(path, "r") as file: return file.readlines()

def write(content, path):

    """This helper function complements `read` and `readlines. It wraps
    `file.write` with an idiomatic with-statement, so we can write to a
    file (creating one if it does not exist) in a single expression. The
    function takes two required args (`path` and `content`). The content
    can be any object. It is passed to `str`, then written to the file
    (replacing anything the file may have already contained) specified
    by the path. Once complete, this function returns `None`."""

    with open(path, "w+") as file: file.write(str(content))

def flatten(structure, terminal=None):

    """This function flattens a nested sequence, returning the result as
    an instance of the `Nodes` class (a pure superset of `list`). Having
    this function return a `Nodes` instance instead of being a generator
    is just more convenient in practice (as we always need an instance
    `Nodes` in practice). Practicality beats purity.

    This function is important to the internal API, where it is used to
    flatten sequences of child nodes passed to element constructors and
    all of the child operators. Users can also use it if they want to.

    The first arg (`structure`) is required, and is the object that needs
    flattening. The second arg (`terminal`) is optional. If provided, it
    is used instead of the default function that determines if an item is
    terminal or not. It defaults to a function that treats lists, tuples
    and any of their derived classes (including `Nodes`) as recursive,
    and all other types of object as terminal:

    >>> flatten([0, [], 1, 2, (3), (4, 5, [6]), 7, ((())), [[], 8], [[9]]])
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    Special Case: Generator arguments are internally passed to `tuple`, so
    they are effectively non-terminal:

    >>> flatten(n * 2 for n in (1, 2, 3))
    [2, 4, 6]

    Aside: Other Python Hypertext DSLs use flattening as a core concept. In
    HTME, flattening just happens automatically."""

    results = Nodes() # the list of results that will be returned

    # Set the function that determines if an item is terminal or non-terminal:
    terminal = terminal or (lambda item: not isinstance(item, (list, tuple)))

    for item in structure:

        # Prevent dicts from being accidently provided as children:
        if isinstance(item, dict): raise ValueError("dicts cannot be children")

        # Invoke element classes to convert them to element instances:
        if type(item) is type and issubclass(item, _Element): item = item()

        # Convert generators to tuples (so generator expressions work as args):
        elif isinstance(item, GeneratorType): item = tuple(item)

        # Append a terminal or recursively flattened non-terminal to `results`:
        results += [item] if terminal(item) else flatten(item)

    return results

def cat(sequence, seperator=""):

    """This function takes one required arg (`sequence`) and an optional arg
    (`seperator`) that defaults to an empty string. Each item in the sequence
    is passed to `str` and all of the results are concatenated together using
    the seperator. The result of the concatenation is returned:

    >>> print(cat(["<", "spam", ">"]))
    <spam>

    >>> print(cat(("spam", "eggs", "spam and eggs"), space))
    spam eggs spam and eggs

    This function is used extensively throughout the library, just because
    it is often a bit prettier than using `join` directly, especially with
    the default seperator."""

    return seperator.join(str(item) for item in sequence)

def ext(path, length=1):

    """This helper takes a required arg (`path`), which should be a path
    or filename string. By default, this function returns everything after
    the last dot in the path. It is useful for getting an extension from
    a filename:

    >>> print(ext("/static/jquery.min.js"))
    js

    The function takes an optional second arg (`length`) that defaults to `1`.
    The length must be a positive integer, and is the number of subextensions
    to include in the output. If there are more than one, the dots in between
    the subextensions are included as well.

    >>> print(ext("/static/jquery.min.js", 2))                       
    min.js
    
    This function is used by `Favicon` to automatically generate the `type`
    attribute from the `path` argument."""

    # split on dots, get `length` parts from the end, join on dots, return

    return cat(path.split(dot)[-length:], dot)

# The concrete container classes...

class Pairs(dict):
    
    """This class complements `Nodes`. It inherits from `dict`, while `Nodes`
    inherits from `list`. Both classes extended their base classes without
    modifying any inherited functionality. Elements with `attributes` use
    a `Pairs` instance. Those with `children` use `Nodes`. We extend the
    builtin containers to make them HTML aware."""

    def sorted(self):

        """This method takes no args. It works a lot like the `dict.items`
        method, returning two-tuples of key, value pairs.
        
        This method implements a lot of the HTME attribute rendering logic
        (simplifying `Configurable.render_attributes`) with three stages:

        1) The method first expands the names of any data attributes that use
        the dollar syntax.

        2) The method then sorts attributes (putting element attributes before
        data attributes, sorting each subset asciibetically by name).

        3) The method then simplifies and escapes the values, so they are the
        exact strings that will be rendered (or `None`).

        Note: The term *sequential value* refers to values that are instances
        of `tuple`, `list` or a subclass. It does not include strings.

        The rest of this docstring contains examples of the different aspects
        of the attribute rendering logic...

        Attribute names that start with a dollar (`$`) are *data attributes*.
        The dollar will be automatically replaced in the rendered output with
        the string `data` followed by a hyphen:

        >>> DIV({"$visitors": "50000"})
        <div data-visitors="50000"></div>

        Attribute names are rendered in asciibetical order:

        >>> DIV({"aa": "0", "bb": "3", "ab": "1", "ba": "2"})
        <div aa="0" ab="1" ba="2" bb="3"></div>

        The element attribute's are rendered before any data attributes:

        >>> DIV({"aa": "0", "$bb": "3", "$ab": "2", "ba": "1"})
        <div aa="0" ba="1" data-ab="2" data-bb="3"></div>

        Note: Sorting attribute names in the output is important to making the
        rendering process deterministic.

        If an attribute's value is a bool, it is converted to a string and
        then converted to lowercase:

        >>> DIV({"true": True, "false": False})
        <div false="false" true="true"></div>

        Numerical values are converted to strings:

        >>> DIV({"aa": 0, "bb": 3, "ab": 1, "ba": 2})
        <div aa="0" ab="1" ba="2" bb="3"></div>

        If an attribute's value is a list or tuple (or any subclass), then
        each of the values in the sequence are converted according to the
        same rules as single values, then joined with spaces to form the
        string used in the output:

        >>> attributes = {"viewbox": (1, 1, 100, 100)}
        >>> attributes["xmlns"] = "http://www.w3.org/2000/svg"
        >>> SVG(attributes)
        <svg viewbox="1 1 100 100" xmlns="http://www.w3.org/2000/svg"></svg>

        Null values are special. If an attribute's value is `None` it will be
        left unchanged (the value will still be `None` in the two-tuple that
        is returned by this method). This allows `render_attributes` to omit
        nullified attributes:

        >>> DIV({"class": None})
        <div></div>

        If a value is sequential and any of its subvalues are `None`, those
        values are omitted from the generated string:

        >>> DIV({"test": ("string", 1, [2, 3], None)})
        <div test="string 1 2 3"></div>

        >>> DIV({"test": (0, None, 1, [2, 3], None)})
        <div test="0 1 2 3"></div>

        Attribute values are escaped in the expectation that they will be
        wrapped in double quotes (as `_Configurable.render_attributes` does)
        All open angle brackets, ampersands and doublequotes are escaped
        automatically:

        >>> div = DIV({"foo": "spam & eggs", "bar": '<>"'})
        >>> print(div.render_attributes().strip())
        bar="&lt;>&quot;" foo="spam &amp; eggs"
        """

        def expand(key):

            """This internal helper takes a key that may be spelled using the
            shorthand for data attributes (using the dollar prefix). If it is,
            the dollar is replaced with the `data` prefix and a hyphen. The
            function returns the key (expanded or unchanged)."""

            return "data-" + key[1:] if key.startswith(dollar) else key

        def convert(value):

            """This internal helper function takes an attribute value or the
            subvalue in a sequential value. It returns the equivalent value,
            according to the HTME attribute rendering logic (which is always
            a string or `None`):

            * If `value` is `None`, it is returned.
            * If `value` is `True`, the string `true` is returned. If `value`
              is `False`, the string `false` is returned (note the case).
            * If `value` is a number, the `str` version of `value` is returned.
            * The subvalues in sequences (that are not `None`) are recursively
              converted according to the same rules as terminal values, then
              joined on spaces. The resulting string is returned.
            * If none of the above, `value` is passed to `str` to ensure it
              is a string, then any open angle brackets, ampersands and
              doublequotes are replaced with escape codes (like `&amp;`)    """

            # map the characters that need escaping to their escape codes...
 
            escapees = {'<': '&lt;', '&': '&amp;', '"': '&quot;'}

            if value is None: return value                          # None
            if value is True: return "true"                         # True
            if value is False: return "false"                       # False
            if isinstance(value, (int, float)): return str(value)   # Number
            if isinstance(value, (list, tuple)):                    # Array

                values = (convert(each) for each in value if each is not None)
                return cat(values, space) 

            return cat(escapees.get(char, char) for char in str(value))

        # the data attributes follow any element attributes in the output,
        # so they are collected into two lists and sorted independently...

        element_attributes, data_attributes = [], []

        # iterate over the attributes, expanding keys and converting values,
        # creating the two-tuples, and appending each to the correct list...

        for key, value in self.items():

            key, value = expand(key), convert(value)

            if key.startswith("data-"): data_attributes.append((key, value))
            else: element_attributes.append((key, value))

        # sort both lists of tuples, concatenate them together and return the
        # result (`sort` operates on the first item in each tuple (the key),
        # and the result is asciibetical)...

        element_attributes.sort()
        data_attributes.sort()

        return element_attributes + data_attributes

class Nodes(list):

    """This class extends `list` without overriding any of the inherited
    functionality. The `Pairs` class has a docstring that which explains
    how `Pairs` and `Nodes` compliment each other.
    
    Each element's `children` attribute is an instance of this class.

    Slice operations on an element's children evaluate to an instance of
    this class, which implements operations on slices (operating on each
    element in the slice that supports the operator), for example:

        element[1:-1] **= {"class": "selected"}

    That code updates the class of all but the first and last child of
    `element`, skipping any children that do not have attributes."""

    @property
    def configurable_elements(self):

        """This property returns an iterable of the children in the list
        that are instances of `_Configurable`:

        >>> children = DIV(P("ElementA"), "ElementB", P("ElementC"))[:]
        >>> for element in children.configurable_elements: print(element)
        <p>ElementA</p>
        <p>ElementC</p>
        """

        return (child for child in self if isinstance(child, _Configurable))

    @property
    def parental_elements(self):

        """This property returns an iterable of the children in the list
        that are instances of `_Parental`:

        >>> children = DIV(IMG({"src": "img.png"}), "Text", P("Open"))[:]
        >>> for element in children.parental_elements: print(element)
        <p>Open</p>
        """

        return (child for child in self if isinstance(child, _Parental))

    def __ipow__(self, attributes):

        """This method implements the `**=` operator:

        >>> div = DIV(P("ALI"), P("BOB"), P("CAZ"))
        >>> div[1:] **= {"class": "foo"}
        >>> div
        <div><p>ALI</p><p class="foo">BOB</p><p class="foo">CAZ</p></div>
        """

        for child in self.configurable_elements: child **= attributes

    def __ifloordiv__(self, attributes):

        """This method implements the `//=` operator:

        >>> div = DIV(P("ALI"), P({"class": "foo"}, "BOB"), P("CAZ"))
        >>> div[1:] //= {"class": "bar"}
        >>> div
        <div><p>ALI</p><p class="bar">BOB</p><p class="bar">CAZ</p></div>
        """

        for child in self.configurable_elements: child //= attributes

    def __imul__(self, families):

        """This method implements the `*=` operator:

        >>> div = DIV(P("ALI"), P("BOB"))
        >>> div[:] *= SPAN("SUB")
        >>> div
        <div><p>ALI<span>SUB</span></p><p>BOB<span>SUB</span></p></div>
        """

        for child in self.parental_elements: child *= families

    def __idiv__(self, families):

        """This method implements the `/=` operator:

        >>> div = DIV(P("ALI"), P("BOB"))
        >>> div[:] /= SPAN("SUB")
        >>> div
        <div><p><span>SUB</span></p><p><span>SUB</span></p></div>
        """

        for child in self.parental_elements: child /= families

    def __getitem__(self, arg):

        """This method overrides `list.__getitem__` to ensure slices of
        slices recursively evaluate to `Nodes` (not `list`), which
        depends on this method in Python 3.
        
        >>> DIV(P("ALI"), P("BOB"), P("CAZ"))[:][1]
        <p>BOB</p>

        Note: Python invokes different methods to handle slice operations,
        depending on whether it is Python 2 or 3."""

        result = super(Nodes, self).__getitem__(arg)
        return Nodes(result) if type(result) is list else result

    def __setitem__(self, *args):

        """This method ensures slices of slices recursively evaluate to
        `Nodes` (not `list`) in Python 3.

        >>> children = DIV(P("ALI"), P("BOB"), P("CAZ"))[:-1]
        >>> children[1] = ASIDE("REPLACEMENT")
        >>> children
        [<p>ALI</p>, <aside>REPLACEMENT</aside>]

        >>> SECTION(children)
        <section><p>ALI</p><aside>REPLACEMENT</aside></section>

        Note: Python invokes different methods to handle slice operations,
        depending on whether it is Python 2 or 3."""

        if type(args[0]) is slice: return self[args[0]]
        else: super(Nodes, self).__setitem__(*args)

    def __getslice__(self, start, end=None):

        """This method ensures slices of slices recursively evaluate to
        `Nodes` (not `list`) in Python 2.

        >>> div = DIV(P("ALI"), P("BOB"))
        >>> type(div[:]).__name__
        'Nodes'

        >>> type(div[:][:]).__name__
        'Nodes'

        Note: Python invokes different methods to handle slice operations,
        depending on whether it is Python 2 or 3."""

        return Nodes(self[slice(start, end)])

    def __setslice__(self, start, end, other):
        
        """This method ensures slices of slices recursively evaluate to
        `Nodes` (not `list`) in Python 2:
        
        >>> div = DIV(P("ALI"), P({"class": "foo"}, "BOB"), P("CAZ"))
        >>> div[1:][:] **= {"class": "bar"}
        >>> div
        <div><p>ALI</p><p class="bar">BOB</p><p class="bar">CAZ</p></div>

        >>> div = DIV(P("ALI"), P("BOB"), P("CAZ"))
        >>> div[1:][:] /= "REPLACEMENT"
        >>> div
        <div><p>ALI</p><p>REPLACEMENT</p><p>REPLACEMENT</p></div>

        Note: Python invokes different methods to handle slice operations,
        depending on whether it is Python 2 or 3."""

        return self[start:end]

    __itruediv__ = __idiv__

    def blit(self, index, *children):

        """This method takes a required arg (`index`), followed by one or more
        children. It swaps the item that is currently at the index with the
        child elements (in the order they were passed in):

        >>> div = DIV(P("A"), P("B"), P("C"))
        >>> div.children.blit(0, SPAN("X"))
        >>> div
        <div><span>X</span><p>B</p><p>C</p></div>
        
        >>> div.children.blit(1, [SPAN("Y"), SPAN("Z")])
        >>> div
        <div><span>X</span><span>Y</span><span>Z</span><p>C</p></div>
        """

        # Flatten the values, then reverse them, so they can be iteratively
        # blitted into the array and end up back in the same order:

        children = flatten(children)
        children.reverse()

        # Remove the single item being blitted over, then insert each of the
        # new items, one by one:

        del self[index]
        for child in children: self.insert(index, child)

# The feature mixins for adding blocks of functionality to the abstract
# element classes...

class _Tagged(object):

    """This mixin provides abstract element classes with support for tag
    names by implementing their `tagname` property."""

    @property
    def tagname(self):

        """This computed property returns the tag name, which is computed
        from a class name by converting it to lowercase, then replacing
        each underscore with a hyphen.
        
        The property is computed so that an element instance can have its
        class reassigned (this is not officially supported, as it is only
        safe if you use a class with the same abstract element class):

        >>> element = LINK()
        >>> element **= {"src": "img.png"}
        >>> element.__class__ = IMG
        >>> element
        <img src="img.png">

        The method iterates over the method resolution order, looking for
        the first class name that does not change when it is converted to
        uppercase. This allows element subclasses to inherit their names
        from a standard element base class (subclasses always include at
        least one lowercase character in their names):

        >>> class Foo(DIV): pass
        >>> Foo()
        <div></div>
        
        Note: If a name starts with an underscore, that character is treated
        as though it is not there (this feature is used internally):

        >>> class _FAKE(VoidElement): pass
        >>> _FAKE()
        <fake>

        >>> class _FAKE(NormalElement): pass
        >>> _FAKE()
        <fake></fake>

        >>> class _FAKE(ForeignElement): pass
        >>> _FAKE()
        <fake/>
        """

        # iterate over the element's class and parent classes in the order
        # of inheritance (the method resolution order (the mro))

        for Class in self.__class__.__mro__:

            name = Class.__name__ # get the name of the class as a string

            # if the name changes when converted to uppercase, it is not a
            # standard element class, so we need to move on to the next one

            if name.upper() != name: continue

            # now we have the right class name, remove any leading underscore
            # (they are only used to prevent internal classes being exported)

            if name[0] == underscore: name = name[1:]

            # convert to lowercase, replace underscores with hyphens, return

            return name.lower().replace(underscore, minus)

class _Configurable(object):

    """This mixin provides abstract element classes with *configurability*.
    It implements attribute operators and the `render_attributes` method.

    If this mixin is used with `_Parental` then `_Parental` should be mixed
    in first. See `_Parental` below for more details."""

    def __ipow__(self, other):

        """This method allows the `**=` operator to be used to merge a dict
        of attributes with the element attributes:

        >>> img = IMG()
        >>> img **= {"src": "img.png"}
        >>> img
        <img src="img.png">
        """

        self.attributes.update(other)
        return self

    def __ifloordiv__(self, other):

        """This method allows the `//=` operator to be used to assign a new
        dict of attributes to `self.attributes`:

        >>> img = IMG({"src": "img.png"})
        >>> img //= {"src": "mugshot.png", "class": "selected"}
        >>> img
        <img class="selected" src="mugshot.png">

        Note: This method mutates the attributes in place.
        Note: This method complements `NormalElement.__idiv__`, which provides
        similar functionality for replacing children."""

        # cannot assign `other` as we need to mutate the container in place

        self.attributes.clear()
        self.attributes.update(other)
        return self

    def __getitem__(self, name):

        """This method allows the square brackets suffix operator to be used
        to access element attributes by name:
        
        >>> img = IMG({"src": "img.png"})
        >>> print(img["src"])
        img.png

        Note: This method complements `NormalElement.__getitem__`, which also
        supports accessing children."""

        return self.attributes[name]

    def __setitem__(self, name, other):

        """This method complements the `Element.__getitem__` method, allowing
        single attributes to be updated:

        >>> img = IMG({"src": "img.png"})
        >>> img["src"] = "mugshot.png"
        >>> print(img["src"])
        mugshot.png

        Note: The `**=` and `//=` operators can update multiple attributes in
        a single invocation."""

        self.attributes[name] = other
        return self

    def __eq__(self, other):

        """This method checks whether two elements are equal by checking that
        they both evaluate to the same string:
        
        >>> x = IMG({"src": "img.png", "class": "selected"})
        >>> y = IMG({"class": "selected", "src": "img.png"})
        >>> x == y
        True
        """

        return repr(self) == repr(other)

    def __ne__(self, other):

        """This method checks that two elements are not equal by checking that
        they both evaluate to different strings:
        
        >>> x = IMG({"src": "img.png", "class": "selected"})
        >>> y = IMG({"class": "selected", "src": "img.png"})
        >>> x != y
        False
        """

        return repr(self) != repr(other)

    def __len__(self):

        """This method complements `NormalElement.__len__`, but it only ever
        returns zero as `VoidElement` instances have no children.
    
        >>> len(IMG({"src": "img.png"})) == 0
        True
        """

        return 0

    def render_attributes(self):

        """This helper method renders the attributes dict, as the attributes
        would be appear in a HTML opening tag.

        This method is generally only used internally, though users can access
        it if they want to use it.

        If an attribute has an empty string as its value, the method
        outputs it as a boolean attribute.

        >>> DIV({"contenteditable": ""})
        <div contenteditable></div>

        If an attribute's value is `None`, the attribute is not rendered
        at all:

        >>> DIV({"foo": None, "bar": "include"})
        <div bar="include"></div>
        """

        if not self.attributes: return ""

        results = []

        for key, value in self.attributes.sorted():

            if value is None: continue                # ignore null attributes
            elif value == "": results.append(key)     # fix boolean attributes
            else: results.append('{}="{}"'.format(key, value))  # normal pairs

        return space + cat(results, space) if results else ""

class _Parental(object):

    """This mixin makes abstract element classes *parental*. It implements
    the child operators and the `render_children` method.

    If this mixin is mixed with the `_Configurable` mixin, then this class
    must come first in the MRO. This class provides methods for getting and
    setting items (using the square brackets operator) that will correctly
    distinguish between keys, indexes and slices. `_Configurable` also
    implements those methods, but they always expect keys."""

    def __imul__(self, *families):

        """This method allows families to be appended to `self.children`,
        using the `*=` operator:

        >>> ul = UL({"class": "nav"})
        >>> ul *= LI("Coffee"), LI("Tea"), LI("Milk")
        >>> print(ul)
        <ul class="nav"><li>Coffee</li><li>Tea</li><li>Milk</li></ul>

        Note: `Document.__imul__` operates the same way, operating on the
        `Document.tree` element."""

        self.children += flatten(families)
        return self

    def __idiv__(self, *families):

        """This method allows families to be assigned to `self.children`,
        replacing any existing children, using the `/=` operator:

        >>> ul = UL(LI("Coffee"), LI("Tea"))
        >>> ul /= LI("Milk")
        >>> print(ul)
        <ul><li>Milk</li></ul>

        Note: This method mutates the list of children in place.

        Note: The `NormalElement.__itruediv__` method is aliased to this one,
        as Python 3 renamed it and changed its semantics (the differences
        do not affect the operator's HTME semantics).

        Note: `Document.__idiv__` maps this method to the tree.         """

        # This is slightly convoluted, but a slice of `Nodes` is not the same
        # instance as the instance it is a slice of, so we have to juggle the
        # values a bit to replace all the children in the original container:

        del self.children[:]
        self.children += flatten(families)
        return self

    def __getitem__(self, arg):

        """This method allows the square brackets suffix operator to be used
        to access element attributes by name and children by index:

        >>> ul = UL({"class": "nav"}, LI("Coffee"), LI("Tea"), LI("Milk"))
        >>> print(ul["class"])
        nav

        >>> print(ul[1])
        <li>Tea</li>

        >>> print(ul[1][0])
        Tea

        The method also supports slicing an element into an instance of
        `Nodes` containing the children expressed by the slice.

        >>> print(UL(LI("Coffee"), LI("Tea"), LI("Milk"))[1:])
        [<li>Tea</li>, <li>Milk</li>]
        
        Note: For doctests operating on slices see, `Nodes`."""

        # If the arg is an int, return the child at that index. If the arg is
        # a slice, return an instance of `Nodes` containing the contents of
        # the slice. Otherwise, treat the arg as an attributes dict key,
        # and return its value:

        if isinstance(arg, int): return self.children[arg]
        elif isinstance(arg, slice): return Nodes(self.children[arg])
        else: return self.attributes[arg]

    def __setitem__(self, arg, other):

        """This method complements `__getitem__`, handling assignments to
        keys, indexes and slices:

        >>> ul = UL({"class": "nav"}, LI("Coffee"), LI("Tea"), LI("Milk"))
        >>> ul["class"] = "buttons"
        >>> ul[1] = P("replacement")
        >>> print(ul)
        <ul class="buttons"><li>Coffee</li><p>replacement</p><li>Milk</li></ul>

        >>> ul = UL(DIV("content"))
        >>> ul[0] = LI(), LI(), LI()
        >>> print(ul)
        <ul><li></li><li></li><li></li></ul>

        Note: For doctests operating on slices see, `Nodes`."""

        # This makes the same distinction as `__getitem__`, but assigns to
        # the index, attribute or list of `Nodes` expressed by a slice:

        if isinstance(arg, int): self.children.blit(arg, other)
        elif isinstance(arg, slice): return Nodes(self.children[arg])
        else: self.attributes[arg] = other

    def __len__(self):

        """This method implements `len(element)`, returning the total number
        of children the element has:
        
        >>> ul = UL({"class": "nav"}, LI("Coffee"), LI("Tea"), LI("Milk"))
        >>> len(ul) == 3
        True
        """

        return len(self.children)

    def __iter__(self):

        """This method allows iteration over an open element's children (by
        doing something like `child for child in element`):

        >>> ul = UL(LI("Coffee"), LI("Tea"), LI("Milk"))
        >>> for li in ul: print(li)
        <li>Coffee</li>
        <li>Tea</li>
        <li>Milk</li>
        """

        for child in self.children: yield child

    __itruediv__ = __idiv__

    def render_children(self):

        """This method complements `_Configurable.render_attributes`, and
        turns the list of children into HTML by simply concatenating them
        all together:

        >>> ul = UL(LI("Coffee"), LI("Tea"), LI("Milk"))
        >>> print(ul.render_children())
        <li>Coffee</li><li>Tea</li><li>Milk</li>

        This method is generally used internally, though it is exposed to
        users, so they can use it if they wish."""

        return cat(self.children)

class Signature0(object):

    def __init__(self, attributes=None):

        """This method implements Signature 0, which just takes an optional
        attributes dict:

        >>> IMG()
        <img>

        >>> IMG({"src": "img.png"})
        <img src="img.png">
        """

        # TODO: Consider assigning the `Pairs` class to the attributes dict
        # (if it is provided), directly updating its class.

        self.attributes = Pairs({} if attributes is None else attributes)
        self.freezer = {}

class Signature1(object):

    def __init__(self, *children):

        """This method implements the Signature 1, which takes zero or
        more children:

        >>> print(UL({"class": "nav"}, LI("Coffee"), LI("Tea"), LI("Milk")))
        <ul class="nav"><li>Coffee</li><li>Tea</li><li>Milk</li></ul>
        """
   
        self.children = flatten(children)
        self.freezer = {}

class Signature2(object):

    def __init__(self, *args):

        """This method implements Signature 2, which takes an optional
        attibutes dict, followed by zero or more children:

        >>> print(UL({"class": "nav"}, LI("Coffee"), LI("Tea"), LI("Milk")))
        <ul class="nav"><li>Coffee</li><li>Tea</li><li>Milk</li></ul>
        """

        # TODO: See the comment in `Signature0` re. assigning `Pairs`.

        args = list(args)
        attributes = args.pop(0) if args and isinstance(args[0], dict) else {}
        self.attributes = Pairs(attributes)    
        self.children = flatten(args)
        self.freezer = {}

# The abstract element base class...

class _Element(object):

    """This is the abstract base class that all elements ultimately inherit
    from. It implements the common functionality (the freezer and `write`
    method) that all elements support."""

    def __call__(self, key, *args, **kargs):

        """This method makes it possible to access and format frozen elements
        by invoking the instance, passing in the key for the frozen element.
        Users can also pass args and keyword args, which just get passed on
        to the `str.format` method, which is called on the frozen string
        before it is returned:
        
        >>> img = IMG({"src": "{IMG}.png"})
        >>> img.freeze("foo")
        >>> print(img("foo", IMG="mugshot"))
        <img src="mugshot.png">
        """

        return self.freezer[key].format(*args, **kargs)
    
    def freeze(self, key):

        """This method freezes the current state of the element, turning it
        into a string of HTML. The one required arg is the key used to store
        the frozen element in `self.freezer`.
        
        >>> key = "image element"
        >>> img = IMG({"src": "{IMG}"})
        >>> img.freeze(key)
        >>> print(img(key, IMG="img.png"))
        <img src="img.png">
        """

        self.freezer[key] = str(self)

    def write(self, path):

        """This method renders the element and writes it to the given path."""

        write(str(self), path)

# The abstract element classes...

class SpecialElement(_Element, _Parental, Signature1):

    """This abstract element class implements special elements like comments,
    CDATA and Legacy elements (those that have constant opening and closing
    tags, with some raw content between)."""

    def __repr__(self):

        """This method renders special elements. It just concatenates the
        `opener`, `children` and `closer` together."""

        children = self.render_children()
        return "{0}{1}{2}".format(self.opener, children, self.closer)

class VoidElement(_Element, _Tagged, _Configurable, Signature0):

    """This abstract element class implements void elements like IMG and BR
    elements (those that can never have children or raw content, and close
    automatically)."""

    def __repr__(self):

        """This method renders void elements, and uses the void grammar:

            <tagname attributes>                                            """

        attributes = self.render_attributes()
        return "<{0}{1}>".format(self.tagname, attributes)

class NormalElement(_Element, _Tagged, _Parental, _Configurable, Signature2):

    """This abstract element class implements normal elements like DIV and P
    elements (those that always use the normal grammar, even when they have
    no children)."""

    def __repr__(self):

        """This method renders normal elements, and uses the normal grammar:

            <tagname attributes>children</tagname>                          """

        children = self.render_children()
        attributes = self.render_attributes()
        return "<{0}{1}>{2}</{0}>".format(self.tagname, attributes, children)

class ForeignElement(_Element, _Tagged, _Parental, _Configurable, Signature2):

    """This abstract element class implements foreign elements like RECT and
    CIRCLE elements (those that can optionally self-close when they have no
    children)."""

    def __repr__(self):

        """This method renders foreign elements. It uses the normal grammar
        when there are one or more children:

            <tagname attributes>children</tagname>

        It uses the self-closing grammar when there are no children:

            <tagname attributes/>                                           """

        attributes = self.render_attributes()

        return "<{0}{1}/>".format(self.tagname, attributes)

        children = self.render_children()

        return "<{0}{1}>{2}</{0}>".format(self.tagname, attributes, children)

# The concrete Void Element classes...

class AREA(VoidElement): pass
class BASE(VoidElement): pass
class BR(VoidElement): pass
class COL(VoidElement): pass
class EMBED(VoidElement): pass
class HR(VoidElement): pass
class IMG(VoidElement): pass
class INPUT(VoidElement): pass
class LINK(VoidElement): pass
class META(VoidElement): pass
class PARAM(VoidElement): pass
class SOURCE(VoidElement): pass
class TRACK(VoidElement): pass
class WBR(VoidElement): pass

# The concrete Normal Element classes...

class A(NormalElement): pass
class ABBR(NormalElement): pass
class ADDRESS(NormalElement): pass
class APPLET(NormalElement): pass
class ARTICLE(NormalElement): pass
class ASIDE(NormalElement): pass
class AUDIO(NormalElement): pass
class B(NormalElement): pass
class BDI(NormalElement): pass
class BDO(NormalElement): pass
class BLOCKQUOTE(NormalElement): pass
class BODY(NormalElement): pass
class BUTTON(NormalElement): pass
class CANVAS(NormalElement): pass
class CAPTION(NormalElement): pass
class CITE(NormalElement): pass
class CODE(NormalElement): pass
class COLGROUP(NormalElement): pass
class CONTENT(NormalElement): pass
class DATA(NormalElement): pass
class DATALIST(NormalElement): pass
class DD(NormalElement): pass
class DEL(NormalElement): pass
class DESC(NormalElement): pass
class DETAILS(NormalElement): pass
class DFN(NormalElement): pass
class DIALOG(NormalElement): pass
class DIR(NormalElement): pass
class DIV(NormalElement): pass
class DL(NormalElement): pass
class DT(NormalElement): pass
class ELEMENT(NormalElement): pass
class EM(NormalElement): pass
class FIELDSET(NormalElement): pass
class FIGCAPTION(NormalElement): pass
class FIGURE(NormalElement): pass
class FOOTER(NormalElement): pass
class FORM(NormalElement): pass
class H1(NormalElement): pass
class H2(NormalElement): pass
class H3(NormalElement): pass
class H4(NormalElement): pass
class H5(NormalElement): pass
class H6(NormalElement): pass
class HEAD(NormalElement): pass
class HEADER(NormalElement): pass
class HGROUP(NormalElement): pass
class HTML(NormalElement): pass
class I(NormalElement): pass
class INS(NormalElement): pass
class KBD(NormalElement): pass
class LABEL(NormalElement): pass
class LEGEND(NormalElement): pass
class LI(NormalElement): pass
class MAIN(NormalElement): pass
class MAP(NormalElement): pass
class MARK(NormalElement): pass
class MENU(NormalElement): pass
class MENUITEM(NormalElement): pass
class METER(NormalElement): pass
class NAV(NormalElement): pass
class NOBR(NormalElement): pass
class NOEMBED(NormalElement): pass
class NOSCRIPT(NormalElement): pass
class OBJECT(NormalElement): pass
class OL(NormalElement): pass
class OPTGROUP(NormalElement): pass
class OPTION(NormalElement): pass
class OUTPUT(NormalElement): pass
class P(NormalElement): pass
class PICTURE(NormalElement): pass
class PRE(NormalElement): pass
class PROGRESS(NormalElement): pass
class Q(NormalElement): pass
class RP(NormalElement): pass
class RT(NormalElement): pass
class RTC(NormalElement): pass
class RUBY(NormalElement): pass
class S(NormalElement): pass
class SAMP(NormalElement): pass
class SCRIPT(NormalElement): pass
class SECTION(NormalElement): pass
class SELECT(NormalElement): pass
class SHADOW(NormalElement): pass
class SLOT(NormalElement): pass
class SMALL(NormalElement): pass
class SPAN(NormalElement): pass
class STRONG(NormalElement): pass
class STYLE(NormalElement): pass
class SUB(NormalElement): pass
class SUMMARY(NormalElement): pass
class SUP(NormalElement): pass
class SVG(NormalElement): pass
class TABLE(NormalElement): pass
class TBODY(NormalElement): pass
class TD(NormalElement): pass
class TEMPLATE(NormalElement): pass
class TEXTAREA(NormalElement): pass
class TFOOT(NormalElement): pass
class TH(NormalElement): pass
class THEAD(NormalElement): pass
class TIME(NormalElement): pass
class TITLE(NormalElement): pass
class TR(NormalElement): pass
class TT(NormalElement): pass
class U(NormalElement): pass
class UL(NormalElement): pass
class VAR(NormalElement): pass
class VIDEO(NormalElement): pass

# The concrete Foreign Element classes...

class ANIMATE(ForeignElement): pass
class ANIMATEMOTION(ForeignElement): pass
class ANIMATETRANSFORM(ForeignElement): pass
class CIRCLE(ForeignElement): pass
class CLIPPATH(ForeignElement): pass
class COLOR_PROFILE(ForeignElement): pass
class DEFS(ForeignElement): pass
class DISCARD(ForeignElement): pass
class ELLIPSE(ForeignElement): pass
class FEBLEND(ForeignElement): pass
class FECOLORMATRIX(ForeignElement): pass
class FECOMPONENTTRANSFER(ForeignElement): pass
class FECOMPOSITE(ForeignElement): pass
class FECONVOLVEMATRIX(ForeignElement): pass
class FEDIFFUSELIGHTING(ForeignElement): pass
class FEDISPLACEMENTMAP(ForeignElement): pass
class FEDISTANTLIGHT(ForeignElement): pass
class FEDROPSHADOW(ForeignElement): pass
class FEFLOOD(ForeignElement): pass
class FEFUNCA(ForeignElement): pass
class FEFUNCB(ForeignElement): pass
class FEFUNCG(ForeignElement): pass
class FEFUNCR(ForeignElement): pass
class FEGAUSSIANBLUR(ForeignElement): pass
class FEIMAGE(ForeignElement): pass
class FEMERGE(ForeignElement): pass
class FEMERGENODE(ForeignElement): pass
class FEMORPHOLOGY(ForeignElement): pass
class FEOFFSET(ForeignElement): pass
class FEPOINTLIGHT(ForeignElement): pass
class FESPECULARLIGHTING(ForeignElement): pass
class FESPOTLIGHT(ForeignElement): pass
class FETILE(ForeignElement): pass
class FETURBULENCE(ForeignElement): pass
class FILTER(ForeignElement): pass
class FONT(ForeignElement): pass
class FOREIGNOBJECT(ForeignElement): pass
class G(ForeignElement): pass
class HATCH(ForeignElement): pass
class HATCHPATH(ForeignElement): pass
class IMAGE(ForeignElement): pass
class LINE(ForeignElement): pass
class LINEARGRADIENT(ForeignElement): pass
class MARKER(ForeignElement): pass
class MASK(ForeignElement): pass
class MESH(ForeignElement): pass
class MESHGRADIENT(ForeignElement): pass
class MESHPATCH(ForeignElement): pass
class MESHROW(ForeignElement): pass
class METADATA(ForeignElement): pass
class MPATH(ForeignElement): pass
class PATH(ForeignElement): pass
class PATTERN(ForeignElement): pass
class POLYGON(ForeignElement): pass
class POLYLINE(ForeignElement): pass
class RADIALGRADIENT(ForeignElement): pass
class RECT(ForeignElement): pass
class SET(ForeignElement): pass
class SOLIDCOLOR(ForeignElement): pass
class STOP(ForeignElement): pass
class SWITCH(ForeignElement): pass
class SYMBOL(ForeignElement): pass
class TEXT(ForeignElement): pass
class TEXTPATH(ForeignElement): pass
class TSPAN(ForeignElement): pass
class USE(ForeignElement): pass
class VIEW(ForeignElement): pass

# The concrete Special Element classes...

class Comment(SpecialElement):

    """This class implements HTML comment elements, as a concrete subclass of
    the `SpecialElement` base class.
    
    >>> Comment("hello world")
    <!--hello world-->
    """

    opener, closer = "<!--", "-->"

class CData(SpecialElement):

    """This class implements CDATA elements, as a concrete subclass of the
    `SpecialElement` base class.
    
    >>> CData("hello world")
    <![CDATA[hello world]]>
    """

    opener, closer = "<![CDATA[", "]]>"

# The magic element classes that are only used by the engine...

class _HTML(NormalElement):

    """This class implements the main `html` element, which has a different
    signature to other elements, and works differently. Instances of this
    element are used to represent the document as a whole (the doctype is
    prepended to this element automatically when it is represented). This
    class is only used internally."""

    def __init__(self, lang, *signature):

        """These elements are created to hold the `head` and `body` elements
        of a document. The constructor takes a `lang` argument, which sets
        the `lang` attribute of the `html` element. It also takes a `head`
        and `body` element, which become its only children. All three
        arguments are required."""

        super(_HTML, self).__init__(*signature)
        if lang is not None: self["lang"] = lang

    def __repr__(self):
    
        """This overrides `NormalElement.__repr__` so the representation can be
        concatenated to the HTML5 doctype to create a complete document."""

        return "<!doctype html>" + super(_HTML, self).__repr__()

class _BODY(NormalElement):

    """This class implements the `body` element, which is only directly used
    internally (but exposed to library users as `Document.body`).
    
    The constructor takes a reference to the instance of `Document` that the
    body element is bound to. The reference is used by the `__repr__` method
    to append the augmentation to the body. The remaining arguments have the
    same signature as standard normal elements."""

    def __init__(self, document, *signature):

        super(_BODY, self).__init__(*signature)
        self.document = document

    def __repr__(self):

        """This overrides `NormalElement.__repr__` so that the augmentation
        can be automatically appended to the body in the rendered output."""

        children = self.render_children()
        attributes = self.render_attributes()
        augmentation = self.document.render_augmentation()
        args = self.tagname, attributes, children, augmentation
        return "<{0}{1}>{2}{3}</{0}>".format(*args)

# The Magic Element Helper Classes...

class Tree(NormalElement):

    """This abstract element implements just the body of a proper HTML element.
    It has children, and all the methods that open elements have for working
    with children, but it does not have a name or attributes (nor the
    associated methods).

    When an instance of `Tree` is rendered, it just concatenates each of its
    children together and returns the HTML.

    Note: An instance of this class is exposed to users as `Engine.tree`."""

    def __init__(self): self.children = Nodes()

    def __repr__(self): return self.render_children()

class Legacy(SpecialElement):

    """This class implements the Internet Explorer less-than-or-equal tags
    that render their content if the browser is an older version of IE.

    >>> Legacy(7, P("upgrade"), P("now"))
    <!--[if lte IE 7]><p>upgrade</p><p>now</p><![endif]-->
    """

    closer = "<![endif]-->"

    def __init__(self, version, *children):

        """This method takes a required version number (an integer) and zero
        or more children. The version number is used to create the tags, and
        the children are (potentially) rendered inside it."""

        self.children = Nodes(children)
        self.opener = "<!--[if lte IE {0}]>".format(version)

class Favicon(META):

    """This class extends `META` with functionality for creating link tags
    for favicons. The constructor takes a path, followed by zero or more
    ints, which (if provided) set the `sizes` attribute, with each size
    converted into the correct syntax. This class assumes all favicons
    are square (providing `16` as a size sets it to `16x16`). When no
    sizes are provided, the filetype should be SVG:

    >>> Favicon("icon.svg")
    <meta href="icon.svg" rel="icon" sizes="any" type="image/svg+xml">

    >>> Favicon("icon.png", 16)
    <meta href="icon.png" rel="icon" sizes="16x16" type="image/png">

    >>> Favicon("icon.png", 64, 128)
    <meta href="icon.png" rel="icon" sizes="64x64 128x128" type="image/png">
    """

    def __init__(self, href, *sizes):

        if not sizes: size, image_type = "any", "image/svg+xml"
        else:

            size = space.join( "{0}x{0}".format(size) for size in sizes )
            image_type = "image/" + ext(href)

        self.attributes = Pairs(
            rel="icon", href=href, sizes=size, type=image_type
        )

class Mobicon(Favicon):

    """This class extends `Favicon` by removing the `type` attribute and
    setting the `rel` attribute to `apple-touch-icon`. These elements were
    created by Apple for specifying the addresses for the various icons used
    by their range of mobile devices. Android has since started using these
    icons as well, so we named them *mobicons*.

    >>> Mobicon("icon.svg")
    <meta href="icon.svg" rel="apple-touch-icon" sizes="any">

    >>> Mobicon("icon.png", 16)
    <meta href="icon.png" rel="apple-touch-icon" sizes="16x16">
    """

    def __init__(self, *args):

        super(Mobicon, self).__init__(*args)
        self["rel"] = "apple-touch-icon"
        self.attributes.pop("type")

class Anchor(A):

    """This class implements a magic element that generates anchor tags. The
    constructor requires a path (the `href` value), followed by the Standard
    Signature:

    >>> Anchor("/about", "The about us page.")
    <a href="/about">The about us page.</a>

    >>> Anchor("/about", {"class": "button"}, "The about us page.")
    <a class="button" href="/about">The about us page.</a>
    """

    def __init__(self, path, *signature):

        super(Anchor, self).__init__(*signature)
        self["href"] = path

class Style(LINK):

    """This class implements a magic element that generates elements for
    loading CSS stylesheets. The constructor requires a url (the `href`
    value) to be passed before an optional attributes dict.

    >>> Style("/static/magic.css")
    <link href="/static/magic.css" rel="stylesheet">
    """

    def __init__(self, path, *signature):

        super(Style, self).__init__(*signature)
        self **= {"rel": "stylesheet", "href": path}

class Logic(SCRIPT):

    """This class implements a magic element that generates elements for
    loading JavaScript scripts. The constructor requires a link (the `href`
    value) to be passed before the regular arguments that all elements take.

    >>> Logic("/static/wizardry.js")
    <script src="/static/wizardry.js"></script>
    """

    def __init__(self, path, *args):

        super(Logic, self).__init__(*args)
        self["src"] = path

# The Hypertext Markup Engine...

class Engine(object): # TODO: improve doctest

    """This class models HTML5 documents. The API is covered in the intro and
    API docs.
    
    Note: The engine methods have doctests, but the engine really needs in an
    external file (`text.htme`) full of example documents to test against. It
    currently only has one simple example, so this is all we have for now:

    >>> docs = Engine(favicon="favicon.png")
    >>> docs.install(Style("magic.css"), Logic("wizardry.js"))
    >>> docs.uninstall(Style("magic.css"))
    >>> docs.title = "404 Error"
    >>> docs.description = "A subpage for file-not-found errors."
    >>> docs *= HEADER(Anchor("/", "Write Dot Run"))
    >>> str(docs) == read("test.htme")
    True

    >>> str(docs) == readlines("test.htme")[0]
    True
    """

    def __init__(

        # four miscellaneous attributes...

        self,
        lang="en",            # required ISO 639-1 language code
        freezer=None,         # optional alternative initial frozen docs
        tree=None,            # optional alternative initial tree element

        # the expandable element attributes...

        charset="utf-8",      # required character encoding
        ie_version="edge",    # optional X-UA-Compatible metatag version
        base=None,            # setting for the optional base element
        title="",             # required body of the title element
        author=None,          # optional content of the author metatag
        description=None,     # optional content of the description metatag
        manifest=None,        # optional url for the web manifest file
        favicon=None,         # optional url for the favicon image file

        # the viewport attributes...

        viewport=True,        # how to handle rendering the viewport metatag
        scale=1,              # sets the `initial-scale` viewport attribute
        scalable=None,        # sets the `user-scalable` viewport attribute
        minimum_scale=None,   # sets the `minimum-scale` viewport attribute
        maximum_scale=None,   # sets the `maximum-scale` viewport attribute
        width="device-width", # sets the `width` viewport attribute
        height=None,          # sets the `height` viewport attribute

        # the three element arrays...

        installation=None,    # list of resource elements appended to the head
        augmentation=None,    # list of resource elements appended to the body
        icons=None,           # list of optional favicon and mobicon elements

        # the attributes dicts for the boilerplate elements...

        html_attributes=None, # the hash for the html element attributes
        head_attributes=None, # the hash for the head element attributes
        body_attributes=None  # the hash for the body element attributes
        
        ):

        """This method has no required args (beyond `self`), and basically
        just copies its keyword args to `self`, handling defaults etc.

        Note that if `freezer` is provided *as a keyword argument*, it can be
        an instance of `_Element` or `Engine`, and its `freezer` attribute is
        shallow copied to this engine. Of course, a dict can also be passed,
        and it will be used directly (without copying)."""

        # This function returns its first arg if its first arg is expressly
        # not `None`; otherwise it returns its second arg:

        extant = lambda arg, default: default if arg is None else arg

        # Directly copy arguments with simple defaults over to `self`:

        self.lang = lang
        self.charset = charset
        self.ie_version = ie_version
        self.base = base
        self.title = title
        self.author = author
        self.description = description
        self.viewport = viewport
        self.scale = scale
        self.scalable = scalable
        self.minimum_scale = minimum_scale
        self.maximum_scale = maximum_scale
        self.width = width
        self.height = height
        self.manifest = manifest
        self.favicon = favicon

        # Use the `extant` function to handle the mutable defaults:

        self.tree = extant(tree, Tree())
        self.icons = extant(icons, [])
        self.installation = extant(installation, [])
        self.augmentation = extant(augmentation, [])
        self.html_attributes = extant(html_attributes, {})
        self.head_attributes = extant(head_attributes, {})
        self.body_attributes = extant(body_attributes, {})

        # Copy the freezer from an element or engine if one is passed in,
        # else use the arg directly (still defaulting to an empty dict):

        if isinstance(freezer, (_Element, Engine)):

            self.freezer = freezer.freezer.copy()

        else: self.freezer = {} if freezer is None else freezer

    def __repr__(self):

        """This method makes the representation of the document render and
        return its HTML representation.
        
        Note: This method always returns a valid HTML5 document.

        Note: The design of the library fundamentally depends on this method
        never mutating `self`."""

        head = HEAD(
            self.head_attributes,       self.render_charset(),
            self.render_ie_version(),   self.render_base(),
            self.render_title(),        self.render_author(),
            self.render_description(),  self.render_viewport(),
            self.render_favicon(),      self.render_icons(),
            self.render_manifest(),     self.render_installation()
        )

        body = _BODY(self, self.body_attributes, str(self.tree))

        return str(_HTML(self.lang, self.html_attributes, head, body))

    def __call__(self, key, *args, **kargs):

        """This method makes it possible to access and format frozen documents
        by invoking the instance, passing in the key for the frozen document.
        Users can also pass args and keyword args, which just get passed on
        to the `str.format` method, which is called on the frozen string
        before it is returned."""

        return self.freezer[key].format(*args, **kargs)

    def __imul__(self, other):

        """This method implements the `*=` operator for documents, so they
        work like elements, passing everything on to `self.tree`."""

        self.tree *= other
        return self

    def __idiv__(self, other):

        """This method implements the `/=` operator for documents, so they
        work like elements, passing everything on to `self.tree`."""

        self.tree /= other
        return self

    def __getitem__(self, index):

        """This method implements the square bracket suffix operator for
        documents, so they work like elements, passing the arguments
        through to `self.tree`."""

        return self.tree[index]

    def __setitem__(self, index, other):

        """This method implements the square bracket suffix operator for
        documents, so they work like elements, passing the arguments
        through to `self.tree`."""

        self.tree[index] = other
        return self

    def __eq__(self, other):

        """This method checks whether two documents are equal by checking
        that they both evaluate to the same string.
        
        >>> a, b = Engine(), Engine()
        >>> a *= P(), P(), P()
        >>> b *= [P, P, P]
        >>> a == b
        True
        """

        return repr(self) == repr(other)

    def __ne__(self, other):

        """This method checks that two documents are not equal by checking
        that they both evaluate to different strings.

        >>> a, b = Engine(), Engine()
        >>> a *= P(), P(), P()
        >>> b *= [P, P, ASIDE]
        >>> a != b
        True
        """

        return repr(self) != repr(other)

    def __len__(self):

        """This method implements `len(docs)`, where `docs` is an instance
        of `Engine`. It returns the total number of elements in the tree.
        
        >>> doc = Engine()
        >>> len(doc) == 0
        True
        >>> doc *= P, P, P
        >>> len(doc) == 3
        True
        """

        return len(self.tree)

    def __iter__(self):

        """This method makes iterating over the engine instance iterate over
        the tree (actually its children).

        >>> doc = Engine()
        >>> doc *= P(), P(), P()
        >>> for child in doc: print(child)
        <p></p>
        <p></p>
        <p></p>
        """

        for child in self.tree: yield child

    def install(self, *tags):
        
        """This method takes any number of elements, and just appends them to
        `self.installation`.
        
        >>> doc = Engine()
        >>> doc.install(Logic("logic.js"))
        >>> print(doc.render_installation())
        <script src="logic.js"></script>
        """

        self.installation += list(tags)

    def augment(self, *tags):
        
        """This method takes any number of elements, and just appends them to
        `self.augmentation`.

        >>> doc = Engine()
        >>> doc.augment(Logic("logic.js"))
        >>> print(doc.render_augmentation())
        <script src="logic.js"></script>
        """

        self.augmentation += list(tags)

    def iconify(self, *elements):

        """This method takes any number of elements, and just appends them
        to `self.icons`.
        
        >>> doc = Engine()
        >>> doc.iconify(Favicon("logo.png", 16))
        >>> print(doc.render_icons())
        <meta href="logo.png" rel="icon" sizes="16x16" type="image/png">
        """

        self.icons += list(elements)

    @staticmethod
    def un(array, args):

        """This static method is used by the `uninstall`, `unaugment` and
        `uniconify` methods. It takes two required (`array` and `args`).

        If `args` is empty, everything is removed from `array` (in place).
        Otherwise, the method iterates over the items in `args`, treating
        each of them in one of two ways, based on whether the arg is an
        integer or not:

        - Integers: The element at that index (when the method was called)
          is deleted from `array` (possibly raising an `IndexError`).
        - Non-Integers: The `remove` method of `array` is invoked, passing
          the item as the only arg (possibly raising a `ValueError`).

        See `uninstall`, `unaugment` and `uniconify` for more information
        on how this method is used, including doctests."""

        if args:

            args = list(args)
            args.sort()

            for offset, arg in enumerate(args):

                if isinstance(arg, int): del array[arg - offset]
                else: array.remove(arg)

        else: del array[:]

    def uninstall(self, *args):

        """This applies the `un` method to the installation list.
        
        >>> doc = Engine(installation=[Style("style.css")])
        >>> doc.uninstall(Style("style.css"))
        >>> print(doc.render_installation())
        <BLANKLINE>
        """

        self.un(self.installation, args)

    def unaugment(self, *args):

        """This applies the `un` method to the augmentation list.
        
        >>> doc = Engine(augmentation=[Logic("logic.js")])
        >>> doc.unaugment(Logic("logic.js"))
        >>> print(doc.render_augmentation())
        <BLANKLINE>
        """

        self.un(self.augmentation, args)

    def uniconify(self, *args):

        """This applies the `un` method to the icons list.
        
        >>> doc = Engine()
        >>> doc.iconify(Favicon("logo.png", 16, 32))
        >>> doc.uniconify(Favicon("logo.png", 16, 32))
        >>> print(doc.render_icons())
        <BLANKLINE>
        """

        self.un(self.icons, args)

    def render_installation(self):

        """This method renders the installation elements (the elements that
        load JavaScript and CSS files at the end of the head element) by
        concatenating the elements in the installation list.

        >>> Engine().render_installation() == empty
        True

        >>> doc = Engine(installation=[Style("style.css")])
        >>> print(doc.render_installation())
        <link href="style.css" rel="stylesheet">
        """

        return cat(self.installation)

    def render_augmentation(self):

        """This method renders the augmentation elements (the elements that
        load JavaScript and CSS files at the end of the body element) by
        concatenating the elements in the augmentation list.

        >>> Engine().render_augmentation() == empty
        True

        >>> doc = Engine(augmentation=[Logic("logic.js")])
        >>> print(doc.render_augmentation())
        <script src="logic.js"></script>
        """

        return cat(self.augmentation)

    @staticmethod
    def expand(candidate, fallback):

        """This static method takes the value of an engine attribute and an
        element (`candidate` and `fallback`), both required. It implements
        the element attribute expansion logic.

        If the candidate is `None`, an empty string is returned. If it is an
        element, then the candidate itself is returned, otherwise the fallback
        is returned.

        This is used internally by many of the internal `Engine.render_*`
        methods (and doctested by them)."""

        if candidate is None: return ""
        if isinstance(candidate, _Element): return candidate
        return fallback

    def render_charset(self):

        """This method expands the meta charset engine attribute:

        >>> Engine().render_charset()
        <meta charset="utf-8">

        >>> Engine(charset="ANSI").render_charset()
        <meta charset="ANSI">
        """

        return self.expand(self.charset, META({"charset": self.charset}))

    def render_ie_version(self):

        """This method expands the `X-UA-Compatible` engine attribute:

        >>> Engine().render_ie_version()
        <meta content="ie=edge" http-equiv="x-ua-compatible">

        >>> Engine(ie_version=7).render_ie_version()
        <meta content="ie=7" http-equiv="x-ua-compatible">

        >>> Engine(ie_version=None).render_ie_version() == empty
        True
        """

        return self.expand(self.ie_version, META({
            "http-equiv": "x-ua-compatible",
            "content": "ie={}".format(self.ie_version)
        }))

    def render_base(self):

        """This method expands the `base` engine attribute:

        >>> Engine().render_base() == empty
        True

        >>> Engine(base="http://www.example.com/page.html").render_base()
        <base href="http://www.example.com/page.html">

        Users wanting to set the `target` attribute must provide an element:

        >>> Engine(base=BASE({"target": "_blank"})).render_base()
        <base target="_blank">
        """

        return self.expand(self.base, BASE({"href": self.base}))

    def render_title(self):

        """This method renders the `title` element, which is required. Its
        content defaults to an empty string:

        >>> Engine().render_title()
        <title></title>

        >>> Engine(title="spam and eggs").render_title()
        <title>spam and eggs</title>
        """

        return TITLE(self.title)

    def render_author(self):

        """This method expands the `author` engine attribute:

        >>> Engine().render_author() == empty
        True

        >>> Engine(author="batman").render_author()
        <meta content="batman" name="author">
        """

        return self.expand(self.author, META({
            "name": "author", "content": self.author
        }))

    def render_description(self):

        """This method expands the `description` engine attribute:

        >>> Engine().render_description() == empty
        True

        >>> Engine(description="spam and eggs").render_description()
        <meta content="spam and eggs" name="description">
        """

        return self.expand(self.description,  META({
            "name": "description", "content": self.description
        }))

    def render_viewport(self):

        """This method renders the viewport META tag that sets the initial
        scale, maximum and minimum scale, scalability, height and width of
        the viewport. This helps mobile devices to render pages correctly.

        If `mobile` is `None`, no element is rendered. Otherwise, the element
        is constructed from the `scale`, `scalable`, `width`, `height`,
        `maximum_scale` and `minimum_scale` attributes:

        >>> doc = Engine()
        >>> doc.render_viewport()
        <meta content="width=device-width, initial-scale=1" name="viewport">

        >>> doc.scale = 1.5
        >>> doc.width = 1280
        >>> doc.render_viewport()
        <meta content="width=1280, initial-scale=1.5" name="viewport">

        >>> doc.scale = None
        >>> doc.height = "device-height"
        >>> doc.render_viewport()
        <meta content="width=1280, height=device-height" name="viewport">

        >>> doc.viewport = META({"name": "viewport", "content": "width=800"})
        >>> doc.render_viewport()
        <meta content="width=800" name="viewport">

        >>> doc.viewport = None
        >>> doc.render_viewport() == empty
        True
        """

        if self.viewport is None: return ""

        if isinstance(self.viewport, _Element): return self.viewport

        values = []

        if self.width is not None:

            values.append("width={0}".format(self.width))

        if self.height is not None:

            values.append("height={0}".format(self.height))

        if self.scale is not None:

            values.append("initial-scale={0}".format(self.scale))

        if self.scalable is not None:

            values.append("user-scalable={0}".format(self.scalable))

        if self.minimum_scale is not None:

            values.append("minimum-scale={0}".format(self.minimum_scale))

        if self.maximum_scale is not None:

            values.append("maximum-scale={0}".format(self.maximum_scale))

        return META({"name": "viewport", "content": cat(values, ", ")})

    def render_favicon(self):

        """This method expands the `favicon` engine attribute:

        >>> Engine().render_favicon() == empty
        True

        >>> Engine(favicon="logo.png").render_favicon()
        <link href="logo.png" rel="icon">
        """

        return self.expand(self.favicon, LINK({
            "rel": "icon", "href": self.favicon
        }))
    
    def render_icons(self):

        """This method renders the elements that link to favicon and mobicon
        image files, based on the items in `icons`.

        >>> doc = Engine()
        >>> doc.iconify(Favicon("logo.png", 16, 32))
        >>> print(doc.render_icons())
        <meta href="logo.png" rel="icon" sizes="16x16 32x32" type="image/png">

        >>> doc = Engine()
        >>> doc.iconify(Mobicon("logo.svg"))
        >>> print(doc.render_icons())
        <meta href="logo.svg" rel="apple-touch-icon" sizes="any">
        """

        return cat(self.icons)

    def render_manifest(self):

        """This method expands the `manifest` engine attribute:

        >>> Engine().render_manifest() == empty
        True

        >>> Engine(manifest="site.webmanifest").render_manifest()
        <link href="site.webmanifest" rel="manifest">
        """

        return self.expand(self.manifest, LINK({
            "rel": "manifest", "href": self.manifest
        }))

    def freeze(self, key):

        """This method freezes the current state of the instance, turning it
        into a string. The one required arg is the key used to store the
        frozen doc in `self.freezer`."""

        self.freezer[key] = str(self)

    def write(self, path):

        """This method converts the instance to a HTML document and writes it
        to the given path."""

        write(str(self), path)

# Run the doctests if this file is executed as a script...

if __name__ == "__main__":

    from doctest import testmod
    print(testmod())
