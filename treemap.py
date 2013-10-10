#!/usr/bin/env python
'''
Creates an html treemap of disk usage, using the Google Charts API
'''

import json
import os
import subprocess
import sys

def memoize(fn):
    stored_results = {}
    def memoized(*args):
        try:
            return stored_results[args]
        except KeyError:
            result = stored_results[args] = fn(*args)
            return result

    return memoized


@memoize
def get_folder_size(folder):
    total_size = os.path.getsize(folder)
    for item in os.listdir(folder):
        itempath = os.path.join(folder, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += get_folder_size(itempath)
    return total_size


def usage_iter(root):
    root = os.path.abspath(root)
    root_size = get_folder_size(root)
    root_string = "{0}\n{1}".format(root, root_size)
    yield [root_string, None, root_size]
    
    for parent, dirs, files in os.walk(root):
        for dirname in dirs:
            fullpath = os.path.join(parent, dirname)
            try:
                this_size = get_folder_size(fullpath)
                parent_size = get_folder_size(parent)
                this_string = "{0}\n{1}".format(fullpath, this_size)
                parent_string = "{0}\n{1}".format(parent, parent_size)
                yield [this_string, parent_string, this_size]
            except OSError:
                continue


def json_usage(root):
    root = os.path.abspath(root)
    result = [['Path', 'Parent', 'Usage']]
    result.extend(entry for entry in usage_iter(root))
    return json.dumps(result)


def main(args):
    '''Populates an html template using JSON-formatted output from the
    Linux 'du' utility and prints the result'''
    html = '''
<html>
  <head>
    <script type="text/javascript" src="https://www.google.com/jsapi"></script>
    <script type="text/javascript">
      google.load("visualization", "1", {packages:["treemap"]});
      google.setOnLoadCallback(drawChart);
      function drawChart() {
        // Create and populate the data table.
        var data = google.visualization.arrayToDataTable(%s);

        // Create and draw the visualization.
        var tree = new google.visualization.TreeMap(document.getElementById('chart_div'));
        tree.draw(data, { headerHeight: 15, fontColor: 'black' });
        }
    </script>
  </head>

  <body>
    <div id="chart_div" style="width: 900px; height: 500px;"></div>
    <p style="text-align: center">Click to descend. Right-click to ascend.</p>
  </body>
</html>
    ''' % json_usage(args[0])
#    ''' % du2json(get_usage(args[0]))
    print html

if __name__ == "__main__":
    main(sys.argv[1:] or ['.'])
