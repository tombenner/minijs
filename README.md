Minijs
=================================================
A JavaScript and CoffeeScript minifier for Django

Description
-----------

Minijs provides a template tag that lets you specify a list of JavaScript and CoffeeScript files that will be minified and concatenated into a single output file (the CoffeeScript files will be compiled, too, of course).

Usage
-----

Here's an example:

    {% load minijs %}
    {% minijs "base_scripts" %}
      path/to/jquery.min.js-
      path/to/jquery.ui.min.js-
      path/to/my_unminified_script1.js
      path/to/my_unminified_script2.js
      path/to/my_coffeescript1.coffee
      path/to/my_coffeescript2.coffee
    {% endminijs %}

This will output a single `<script>` tag that points to a file that contains the minified and concatenated source of all of the input files:

    <script type="text/javascript" src="/static/minijs/stable/base_scripts.js"></script>

The first argument ("base_scripts") is the name of the output file and should be unique for each call.  If you'd like to include JS files that have already been minified and shouldn't be minified again, add a "-" to the end of the path.  The paths are relative to STATIC_ROOT (or MEDIA_ROOT if STATIC_ROOT isn't set).

Please make sure that the CoffeeScript executable is installed.  The command `"coffee"` is used by default, but you can specify a custom path to the command by setting `COFFEESCRIPT_EXECUTABLE = "/path/to/coffee"`.

#### Options

`MINIJS_MODE`

(string)

If this is set to `"production"`, the template tag will simply print out a `<script>` tag that has the path of the minified file, bypassing all of the functionality that checks to see if the file exists or needs to be compiled.  This should only be used in an environment where the minification has already been performed and the input files won't be modified.  Default is `"development"`.

`MINIJS_OUTPUT_DIR`

(string)

This sets the name of the output directory within STATIC_ROOT (or MEDIA_ROOT if STATIC_ROOT isn't set).  Default is `"minijs"`.

`MINIJS_BYPASS`

(boolean)

If this is set to `True`, the template tag will output `<script>` tags for each of the input files, instead of minifying and concatenating them (CoffeeScript files are still compiled, though).  Default is `False`.

`MINIJS_ALWAYS_MINIFY`

(boolean)

If this is set to `True`, minijs will minify and concatenate on each page load, instead of checking to see if that process is necessary (i.e. if the input files have been modified since the last minification).  Default is `False`.

`MINIJS_ALWAYS_COMPILE_COFFEESCRIPT_DURING_BYPASS`

(boolean)

If this and `MINIJS_BYPASS` are both set to `True`, minijs will compile CoffeeScript files on every page load, instead of checking to see if compilation is necessary (i.e. if the input files have been modified since the last compilation).  Default is `False`.

`MINIJS_COMPILE_COFFEESCRIPTS_TOGETHER`

(boolean)

By default, the template tag will concatenate the source of all of the CoffeeScript files and compile that, so that a class from one can reference a class from another.  To compile each CoffeeScript individually, set this to `False`.  Default is `True`.

`COFFEESCRIPT_EXECUTABLE`

(string)

Sets the path to the CoffeeScript executable.  Default is `"coffee"`.