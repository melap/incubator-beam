import argparse
import ast
import re
import urllib.request

def main():
  parser = argparse.ArgumentParser(description='This script scrapes SDK '
                                   'dependency information, puts it into an HTML '
                                   'table, and writes it to a file. This table '
                                   'can be used on the website Python '
                                   'dependencies pages.')

  parser.add_argument('--version', metavar='2.10.0', type=str,
                      required=True, help="""Apache Beam SDK version""")
  parser.add_argument('--output', metavar='output_file.txt', type=str,
                      required=True, help="""output text file to store the table""")
  args = parser.parse_args()

  scraper = DependencyScraper(args)
  scraper.download_requirements()
  scraper.visit_nodes()
  scraper.print_table()

class DependencyScraper(ast.NodeVisitor):

  def __init__(self, args):
    self._dep_list = []
    self._args = args
    self._requirements = ""
    
  def download_requirements(self):
    url = "https://raw.githubusercontent.com/apache/beam/release-{}/sdks/python/setup.py".format(self._args.version)
    print("Fetching " + url)
    response = urllib.request.urlopen(url)
    data = response.read()
    self._requirements = data.decode('utf-8')

  def visit_nodes(self):
    tree = ast.parse(self._requirements)
    self.visit(tree)

  def visit_Assign(self, node):
    for assign in node.targets:
      if (assign.id == 'REQUIRED_PACKAGES' or assign.id == 'GCP_REQUIREMENTS'):
        for dep in node.value.elts:
          self._dep_list.append(dep.s)
    self.generic_visit(node)

  def print_table(self):
    self._dep_list.sort()

    output_file = open(self._args.output, "w")
    print("Writing file: " + self._args.output)
    output_file.write("<table class=\"table-bordered table-striped\">\n")
    output_file.write("  <tr><th>Package</th><th>Version</th></tr>\n")
    for dep in self._dep_list:
      match_obj = re.match('([^<=>]*)(.*)', dep)
      if match_obj:
        package = match_obj.group(1)
        version = match_obj.group(2)
        version = re.sub('<', '&lt;', version)
        version = re.sub('>', '&gt;', version)
        output_file.write("  <tr><td>" + package + "</td><td>" + version + "</td></tr>\n")
      else:
        print("No match object returned: " + dep)

    output_file.write("</table>\n")
    output_file.close()
    
if __name__ == '__main__':
  main()
  
