class GTemplate:
    def __init__(self):
        from jinja2 import Environment

        self._environment = Environment()

    @property
    def environment(self):
        return self._environment

    @staticmethod
    def load_file(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            result = file.read()
        return result

    @staticmethod
    def get_template_filepath(filename):
        import os

        path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(path, filename)

    def get_template(self, filename):
        return self.environment.from_string(self.load_file(self.get_template_filepath(filename)))


class GReport:
    def __init__(self, filename):
        import xml.etree.ElementTree as ElementTree

        self._tree = ElementTree.parse(filename)

    @property
    def tree(self):
        return self._tree

    @property
    def root(self):
        return self.tree.getroot()

    def parse_to_json(self):
        def _getattr(node, attr):
            return node.attrib[attr]

        json = {
            'name': _getattr(self.root, 'name'),
            'tests': int(_getattr(self.root, 'tests')),
            'failures': int(_getattr(self.root, 'failures')),
            'disabled': int(_getattr(self.root, 'disabled')),
            'passrate': float(),
            'testsuites': list()
        }

        for child in self.root:
            suite = {
                'name': _getattr(child, 'name'),
                'tests': int(_getattr(child, 'tests')),
                'failures': int(_getattr(child, 'failures')),
                'disabled': int(_getattr(child, 'disabled')),
                'passrate': float()
            }

            test = list()
            for testcase in child:
                info = {
                    'name': _getattr(testcase, 'name'),
                    'time': _getattr(testcase, 'time'),
                    'timestamp': _getattr(testcase, 'timestamp').replace('T', ' '),
                    'status': _getattr(testcase, 'status').upper()
                }
                failures = list()
                for failure in testcase:
                    failures.append({
                        'failure': _getattr(failure, 'message')
                    })

                if failures:
                    info['failures'] = failures
                test.append(info)

            suite['testsuite'] = test
            json['testsuites'].append(self._round(suite))

        return self._round(json)

    @staticmethod
    def _round(suite):
        suite['passrate'] = round((suite['tests'] - suite['failures'] - suite['disabled']) / suite['tests'] * 100, 2)
        return suite

    def create_html(self, output, template_file='template.html'):
        json = self.parse_to_json()
        template = GTemplate().get_template(template_file)

        with open(output, 'w', encoding='utf-8') as file:
            file.write(template.render(test_overview=json, test_suites=json['testsuites']))


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', type=str, help='path of an XML file', required=True)
    parser.add_argument('-o', '--output', type=str, help='output file name', required=True)
    args = parser.parse_args()

    try:
        GReport(args.file).create_html(args.output)
    except Exception as e:
        print('greport: error: {}'.format(e))


if __name__ == '__main__':
    main()
