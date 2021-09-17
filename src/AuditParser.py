import os
import re
import json


class AuditParser:

    def __init__(self, name, path=None):
        self.name = name
        self.path = path
        self.rename = None

    def open_file(self):
        if self.path:
            with open(os.path.join(self.path, self.name)) as file:
                lines = file.read()
        else:
            with open(self.name) as file:
                lines = file.read()
        return lines

    def transform_to_json(self):

        lines = AuditParser.open_file(self)
        lines = re.sub('\n', '', lines)
        lines = re.findall('<custom_item>(.*?)<\/custom_item>', lines)

        li = []

        for element in lines:

            mapper = {}
            element = re.sub('\n', '', element)
            element = re.sub('\s+', ' ', element)

            element = element.strip()
            element = re.findall('(\w+)\s:\s(\w+ |".*?")', element)

            for key, value in element:
                mapper[key] = value
            li.append(mapper)

        return li

    def save_to_json(self):

        li = AuditParser.transform_to_json(self)

        if self.rename:
            with open(f'{self.rename}.json', 'w') as outfile:
                json.dump(li, outfile)
        else:
            name_of_json = re.findall('(.*?).audit', self.name)[0]
            with open(f'{name_of_json}.json', 'w') as outfile:
                json.dump(li, outfile)
