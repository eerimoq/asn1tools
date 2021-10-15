EXPECTED = {'MAPEM-PDU-Descriptions': {'extensibility-implied': False,
        'imports': {
            'DSRC': ['MapData'],
            'ITS-Container': ['ItsPduHeader']
        },
        'types': {
            'MAPEM': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'ItsPduHeader',
                    'name': 'header'
                }, {
                    'type': 'MapData',
                    'name': 'map'
                }]
            }
        },
        'values': {},
        'object-classes': {},
        'object-sets': {},
        'tags': 'AUTOMATIC'
    }
}
