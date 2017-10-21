SIMPLE_CLASS = {
    'SimpleClass': {
        'extensibility-implied': False,
        'imports': {},
        'types': {
            'ITEM': {
                'type': 'CLASS',
                'members': [
                    {'name': '&id', 'optional': False, 'type': 'INTEGER'},
                    {'name': '&comment', 'optional': False, 'type': 'IA5String'}
                ]
            },
            'Items': {
                'type': 'ITEM',
                'members': [
                    {'&id': 0, '&comment': 'item 0'},
                    {'&id': 1, '&comment': 'item 1'}
                ]
            },
            'ItemWithConstraints': {
                'type': 'SEQUENCE',
                'members': [
                    {'name': 'id', 'optional': False, 'type': 'ITEM.&id'},
                    {'name': 'comment', 'optional': False, 'type': 'ITEM.&comment'},
                    {'name': 'value', 'optional': False, 'type': 'REAL'}
                ]
            },
            'ItemWithoutConstraints': {
                'type': 'SEQUENCE',
                'members': [
                    {'name': 'id', 'optional': False, 'type': 'ITEM.&id'},
                    {'name': 'comment', 'optional': False, 'type': 'ITEM.&comment'},
                    {'name': 'value', 'optional': False, 'type': 'REAL'}
                ]
            }
        },
        'values': {}
    }
}
