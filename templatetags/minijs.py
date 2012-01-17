from ..settings import MINIJS_OUTPUT_DIR, MINIJS_BYPASS, MINIJS_ALWAYS_MINIFY, MINIJS_ALWAYS_COMPILE_COFFEESCRIPT_DURING_BYPASS, COFFEESCRIPT_EXECUTABLE
from ..jsmin import jsmin
from django.conf import settings
from django.template.base import Library, Node
import os
import logging
import shlex
import subprocess

logger = logging.getLogger('minijs')
register = Library()

@register.tag('minijs')
def coffeescripts(parser, token):
    nodelist = parser.parse(('endminijs',))
    parser.delete_first_token()
    return Minijs(token, nodelist)

class Minijs(Node):

    def __init__(self, token, nodelist):
        self.token = token
        self.nodelist = nodelist
        self.bypass = MINIJS_BYPASS
        self.always_minify = MINIJS_ALWAYS_MINIFY
        self.always_compile_coffeescript = MINIJS_ALWAYS_COMPILE_COFFEESCRIPT_DURING_BYPASS
        try:
            self.static_root = settings.STATIC_ROOT
        except AttributeError:
            self.static_root = settings.MEDIA_ROOT

    def render(self, context):
        token_list = self.token.split_contents()
        output_path = token_list[1].strip('"')
        content = self.nodelist.render(context)
        input_paths = content.split('\n')
        input_paths = [path.strip() for path in input_paths]
        input_paths = filter(None, input_paths)
        if self.bypass:
          output_paths = self.get_bypassed_paths(input_paths)
          tags = ''
          for output_path in output_paths:
            tags += '<script type="text/javascript" src="'+settings.STATIC_URL+output_path+'"></script>\n'
        else:
          output_path = self.minify_files(output_path, input_paths)
          tags = '<script type="text/javascript" src="'+settings.STATIC_URL+output_path+'"></script>'
        return tags
    
    def get_bypassed_paths(self, input_paths):
      output_paths = []
      for relative_input_path in input_paths:
        relative_input_path = relative_input_path.rstrip('-')
        input_path = os.path.join(self.static_root, relative_input_path)
        if not input_path.endswith('.coffee'):
          output_paths.append(relative_input_path)
        else:
          output_directory = os.path.join(self.static_root, MINIJS_OUTPUT_DIR, 'coffee')
          base_filename = os.path.split(input_path)[-1]
          output_path = os.path.join(output_directory, base_filename+'.js')
          compilation_necessary = self.always_compile_coffeescript
          if os.path.exists(output_path):
            output_mtime = os.path.getmtime(output_path)
            compilation_necessary = False
            if os.path.getmtime(input_path) > output_mtime:
              compilation_necessary = True
          if compilation_necessary:
            source_file = open(input_path)
            source = source_file.read()
            source_file.close()
            source = self.compile_coffeescript(source)
            if source is None:
              return None
            self.write_to_file(output_directory, output_path, source)
          output_paths.append(os.path.join(MINIJS_OUTPUT_DIR, 'coffee', base_filename+'.js'))
      return output_paths

    def compile_coffeescript(self, string):
        args = shlex.split('%s -c -s -p' % COFFEESCRIPT_EXECUTABLE)
        p = subprocess.Popen(args, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, errors = p.communicate(string)
        if out:
          return out
        elif errors:
          print 'CoffeeScript compilation error:'
          print errors
          logger.error(errors)
          return None
    
    def write_to_file(self, output_directory, output_path, content):
        if not os.path.exists(output_directory):
          os.makedirs(output_directory)
        output_file = open(output_path, 'w+')
        output_file.write(content)
        output_file.close()

    def minify_files(self, output_path, input_paths):

        output_directory = os.path.join(self.static_root, MINIJS_OUTPUT_DIR, os.path.dirname(output_path))
        full_path = os.path.join(self.static_root, output_path)
        base_filename = os.path.split(output_path)[-1]

        output_path = os.path.join(output_directory, '%s.js' % base_filename)

        if os.path.exists(output_path):
          output_mtime = os.path.getmtime(output_path)
          minification_necessary = self.always_minify
          for input_path in input_paths:
            input_path = os.path.join(self.static_root, input_path)
            input_path = input_path.rstrip('-')
            if os.path.getmtime(input_path) > output_mtime:
              minification_necessary = True
              break
        else:
          minification_necessary = True

        if minification_necessary:
          if os.path.exists(output_path):
            os.remove(output_path)
          concatenated_source = ''
          for input_path in input_paths:
            full_path = os.path.join(self.static_root, input_path)
            filename = os.path.split(full_path)[-1]
            file_minification_necessary = True
            if full_path.endswith('-'):
              full_path = full_path[:-1]
              file_minification_necessary = False
            source_file = open(full_path)
            source = source_file.read()
            source_file.close()
            if full_path.endswith('.coffee'):
              source = self.compile_coffeescript(source)
              if source is None:
                return None
            if file_minification_necessary:
              source = jsmin(source)
            concatenated_source += source+'\n'
          self.write_to_file(output_directory, output_path, concatenated_source)
        
        output_path = output_path[len(self.static_root):].replace(os.sep, '/').lstrip('/')
        return output_path