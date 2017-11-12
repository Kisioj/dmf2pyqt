
class Action:
    id = None
    can_check = False
    command = ""
    group = ""
    index = 1000
    is_checked = False
    is_disabled = False
    name = None  # no default

    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, v)

        if not self.id:
            name = data.get('name', '')
            if '\\t' in name:
                name = name.split('\\t')
                name = name[0]
            self.id = map(lambda string: ''.join(char for char in string if char.isalnum()), name.split())
            self.id = '_'.join(self.id)

    def __repr__(self):
        return '<Action {} {}>'.format(self.id or '', self.name or '')


class Category:
    def __init__(self, data):
        self.name = data.get('name')
        self.id = ''.join(char for char in self.name if char.isalnum())
        self.command = data.get('command')
        self.saved_params = data.get('saved_params')
        self.actions = []
        for action_data in data.get('actions'):
            action = None  # separator
            if action_data['type'] == 'ACTION':
                action = Action(action_data)
            self.actions.append(action)


class MenuBar:
    def __init__(self, data):
        self.id = data.get('id')
        self.groups = data.get('groups', [])
        self.categories = []
        for menu_data in data.get('menus'):
            self.categories.append(Category(menu_data))
