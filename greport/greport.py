import os
import sys
import argparse

from jinja2 import Environment
import xml.etree.ElementTree as ElementTree


class GTemplate:
    def __init__(self):
        self._environment = Environment()

    @property
    def environment(self):
        return self._environment

    @staticmethod
    def load_file(filename):
        with open(filename, 'r') as file:
            result = file.read()
        return result

    @staticmethod
    def get_template_filepath(filename):
        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, filename)

    def get_template(self, filename):
        return self.environment.from_string(self.load_file(self.get_template_filepath(filename)))


class GReport:
    def __init__(self, filename):
        self._tree = ElementTree.parse(filename)

    @property
    def tree(self):
        return self._tree

    @property
    def root(self):
        return self.tree.getroot()

    def parse_to_json(self):
        json = {
            'name': self.root.attrib['name'],
            'tests': int(self.root.attrib['tests']),
            'failures': int(self.root.attrib['failures']),
            'disabled': int(self.root.attrib['disabled']),
            'testsuites': list()
        }

        for child in self.root:
            suite = {
                'name': child.attrib['name'],
                'tests': int(child.attrib['tests']),
                'failures': int(child.attrib['failures']),
                'disabled': int(child.attrib['disabled']),
            }

            test = list()
            for testcase in child:
                info = {
                    'name': testcase.attrib['name'],
                    'time': testcase.attrib['time'],
                    'status': testcase.attrib['status'].upper()
                }
                failures = list()
                for failure in testcase:
                    failures.append({
                        'failure': failure.attrib['message']
                    })

                if failures:
                    info['failures'] = failures
                test.append(info)

            suite['testsuite'] = test
            json['testsuites'].append(suite)

        return json

    def create_html(self, output, template_file='template.html'):
        json = self.parse_to_json()
        template = GTemplate().get_template(template_file)

        with open(output, 'w') as file:
            file.write(template.render(test_overview=json, test_suites=json['testsuites']))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", type=str, help="path of an XML file", required=True)
    parser.add_argument("-o", "--output", type=str, help="output file name", required=True)
    args = parser.parse_args()

    try:
        GReport(args.file).create_html(args.output)
    except Exception as e:
        print('greport: {}'.format(e))
        sys.exit(1)


if __name__ == '__main__':
    main()