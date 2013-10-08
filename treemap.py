#!/usr/bin/env python
'''
Creates an html treemap of disk usage, using the Google Charts API
'''

import json
import os.path
import subprocess
import sys

def get_usage(path):
    '''Returns the output of running the 'du' utility on path'''
    result = subprocess.Popen(['du', path], stdout=subprocess.PIPE)
    return result.communicate()[0]

def du2json(du_output):
    '''Converts the output of 'du' to JSON suitable for the Google Charts
    API'''
    result = [['Path', 'Parent', 'Usage']]
    seen_parents = set()
    for line in du_output.split('\n'):
        try:
            size, path = line.strip().split('\t')
            node_id = path
            parent_id = os.path.dirname(path)
            seen_parents.add(node_id)
            node_size = int(size)
            row = [node_id, parent_id, node_size]
            result.append(row)
        except ValueError:
            continue

    for i in range(len(result)):
        path, parent, usage = result[i]
        if parent != 'Parent' and parent not in seen_parents:
            parent = None
            result[i] = [path, parent, usage]


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
  </body>
</html>
    ''' % du2json(get_usage(args[0]))
    print html

if __name__ == "__main__":
    main(sys.argv[1:] or ['.'])
