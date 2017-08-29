import collections
import copy
from PIL import Image
from PIL.ExifTags import TAGS

class Bar:
    id = None

    def __init__(self, element):
        self.id = element.get('id')
        self.categories = collections.OrderedDict()
        self.groups = []

        for control in element['controls']:
            # attributes = element['attributes']

            group = control.get('group')
            if group and group not in self.groups:
                self.groups.append(group)

            category_name = control.pop('category')
            if category_name in self.categories:
                category = self.categories[category_name]
            else:
                category = Category(category_name)
                self.categories[category_name] = category

            control['category'] = category
            if not control.get('id') and not control.get('name'):
                menu_element = Separator(control)
            else:
                menu_element = Action(control)
            category.elements.append(menu_element)
            # print(menu_element)


class Category:
    name = ""
    id = None

    def __init__(self, name):
        self.name = name
        self.id = ''.join(char for char in name if char.isalnum())
        self.elements = []


class Action:
    id = None
    can_check = False
    command = ""
    group = ""
    index = 1000
    is_checked = False
    is_disabled = False
    name = None  # no default

    def __init__(self, element):
        self.id = element.get('id')
        # attributes = element['attributes']

        if not self.id:
            name = element.get('name', '')
            if '\\t' in name:
                name = name.split('\\t')
                name = name[0]
            self.id = map(lambda string: ''.join(char for char in string if char.isalnum()), name.split())
            self.id = '_'.join(self.id)

        for k, v in element.items():
            setattr(self, k, v)

    def __repr__(self):
        d = copy.deepcopy(self.__dict__)
        del d['category']
        return '{} {}'.format(self.__class__.__name__, d)


class Separator(Action):
    pass
