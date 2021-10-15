EXPECTED = {
    'DSRC': {
        'imports': {
            'ITS-Container': ['Latitude', 'Longitude', 'StationID'],
            'REGION': [
                'Reg-AdvisorySpeed', 'Reg-ComputedLane',
                'Reg-ConnectionManeuverAssist', 'Reg-GenericLane',
                'Reg-IntersectionGeometry', 'Reg-IntersectionState',
                'Reg-LaneAttributes', 'Reg-LaneDataAttribute', 'Reg-MapData',
                'Reg-MovementEvent', 'Reg-MovementState',
                'Reg-NodeAttributeSetXY', 'Reg-NodeOffsetPointXY',
                'Reg-Position3D', 'Reg-RTCMcorrections',
                'Reg-RequestorDescription', 'Reg-RequestorType',
                'Reg-RestrictionUserType', 'Reg-RoadSegment', 'Reg-SPAT',
                'Reg-SignalControlZone', 'Reg-SignalRequest',
                'Reg-SignalRequestMessage', 'Reg-SignalRequestPackage',
                'Reg-SignalStatus', 'Reg-SignalStatusMessage',
                'Reg-SignalStatusPackage'
            ],
            'ElectronicRegistrationIdentificationVehicleDataModule':
            ['Iso3833VehicleType']
        },
        'types': {
            'RegionalExtension': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'REG-EXT-ID-AND-TYPE.&id',
                    'table': {
                        'type': 'Set'
                    },
                    'name': 'regionId'
                }, {
                    'type': 'REG-EXT-ID-AND-TYPE.&Type',
                    'table': ['Set', ['regionId']],
                    'name': 'regExtValue'
                }],
                'parameters': ['Set']
            },
            'MapData': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MinuteOfTheYear',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'MsgCount',
                    'name': 'msgIssueRevision'
                }, {
                    'type': 'LayerType',
                    'name': 'layerType',
                    'optional': True
                }, {
                    'type': 'LayerID',
                    'name': 'layerID',
                    'optional': True
                }, {
                    'type': 'IntersectionGeometryList',
                    'name': 'intersections',
                    'optional': True
                }, {
                    'type': 'RoadSegmentList',
                    'name': 'roadSegments',
                    'optional': True
                }, {
                    'type': 'DataParameters',
                    'name': 'dataParameters',
                    'optional': True
                }, {
                    'type': 'RestrictionClassList',
                    'name': 'restrictionList',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'RTCMcorrections': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MsgCount',
                    'name': 'msgCnt'
                }, {
                    'type': 'RTCM-Revision',
                    'name': 'rev'
                }, {
                    'type': 'MinuteOfTheYear',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'FullPositionVector',
                    'name': 'anchorPoint',
                    'optional': True
                }, {
                    'type': 'RTCMheader',
                    'name': 'rtcmHeader',
                    'optional': True
                }, {
                    'type': 'RTCMmessageList',
                    'name': 'msgs'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SPAT': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MinuteOfTheYear',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'IntersectionStateList',
                    'name': 'intersections'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SignalRequestMessage': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MinuteOfTheYear',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'second'
                }, {
                    'type': 'MsgCount',
                    'name': 'sequenceNumber',
                    'optional': True
                }, {
                    'type': 'SignalRequestList',
                    'name': 'requests',
                    'optional': True
                }, {
                    'type': 'RequestorDescription',
                    'name': 'requestor'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SignalStatusMessage': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MinuteOfTheYear',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'second'
                }, {
                    'type': 'MsgCount',
                    'name': 'sequenceNumber',
                    'optional': True
                }, {
                    'type': 'SignalStatusList',
                    'name': 'status'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'AdvisorySpeed': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'AdvisorySpeedType',
                    'name': 'type'
                }, {
                    'type': 'SpeedAdvice',
                    'name': 'speed',
                    'optional': True
                }, {
                    'type': 'SpeedConfidence',
                    'name': 'confidence',
                    'optional': True
                }, {
                    'type': 'ZoneLength',
                    'name': 'distance',
                    'optional': True
                }, {
                    'type': 'RestrictionClassID',
                    'name': 'class',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'AdvisorySpeedList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'AdvisorySpeed'
                },
                'size': [(1, 16)]
            },
            'AntennaOffsetSet': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B12',
                    'name': 'antOffsetX'
                }, {
                    'type': 'Offset-B09',
                    'name': 'antOffsetY'
                }, {
                    'type': 'Offset-B10',
                    'name': 'antOffsetZ'
                }]
            },
            'ComputedLane': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'LaneID',
                    'name': 'referenceLaneId'
                }, {
                    'type':
                    'CHOICE',
                    'members': [{
                        'type': 'DrivenLineOffsetSm',
                        'name': 'small'
                    }, {
                        'type': 'DrivenLineOffsetLg',
                        'name': 'large'
                    }],
                    'name':
                    'offsetXaxis'
                }, {
                    'type':
                    'CHOICE',
                    'members': [{
                        'type': 'DrivenLineOffsetSm',
                        'name': 'small'
                    }, {
                        'type': 'DrivenLineOffsetLg',
                        'name': 'large'
                    }],
                    'name':
                    'offsetYaxis'
                }, {
                    'type': 'Angle',
                    'name': 'rotateXY',
                    'optional': True
                }, {
                    'type': 'Scale-B12',
                    'name': 'scaleXaxis',
                    'optional': True
                }, {
                    'type': 'Scale-B12',
                    'name': 'scaleYaxis',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'ConnectsToList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'Connection'
                },
                'size': [(1, 16)]
            },
            'ConnectingLane': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'LaneID',
                    'name': 'lane'
                }, {
                    'type': 'AllowedManeuvers',
                    'name': 'maneuver',
                    'optional': True
                }]
            },
            'Connection': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'ConnectingLane',
                    'name': 'connectingLane'
                }, {
                    'type': 'IntersectionReferenceID',
                    'name': 'remoteIntersection',
                    'optional': True
                }, {
                    'type': 'SignalGroupID',
                    'name': 'signalGroup',
                    'optional': True
                }, {
                    'type': 'RestrictionClassID',
                    'name': 'userClass',
                    'optional': True
                }, {
                    'type': 'LaneConnectionID',
                    'name': 'connectionID',
                    'optional': True
                }]
            },
            'ConnectionManeuverAssist': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'LaneConnectionID',
                    'name': 'connectionID'
                }, {
                    'type': 'ZoneLength',
                    'name': 'queueLength',
                    'optional': True
                }, {
                    'type': 'ZoneLength',
                    'name': 'availableStorageLength',
                    'optional': True
                }, {
                    'type': 'WaitOnStopline',
                    'name': 'waitOnStop',
                    'optional': True
                }, {
                    'type': 'PedestrianBicycleDetect',
                    'name': 'pedBicycleDetect',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'DataParameters': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'IA5String',
                    'size': [(1, 255)],
                    'name': 'processMethod',
                    'optional': True
                }, {
                    'type': 'IA5String',
                    'size': [(1, 255)],
                    'name': 'processAgency',
                    'optional': True
                }, {
                    'type': 'IA5String',
                    'size': [(1, 255)],
                    'name': 'lastCheckedDate',
                    'optional': True
                }, {
                    'type': 'IA5String',
                    'size': [(1, 255)],
                    'name': 'geoidUsed',
                    'optional': True
                }, None]
            },
            'DDateTime': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DYear',
                    'name': 'year',
                    'optional': True
                }, {
                    'type': 'DMonth',
                    'name': 'month',
                    'optional': True
                }, {
                    'type': 'DDay',
                    'name': 'day',
                    'optional': True
                }, {
                    'type': 'DHour',
                    'name': 'hour',
                    'optional': True
                }, {
                    'type': 'DMinute',
                    'name': 'minute',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'second',
                    'optional': True
                }, {
                    'type': 'DOffset',
                    'name': 'offset',
                    'optional': True
                }]
            },
            'EnabledLaneList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'LaneID'
                },
                'size': [(1, 16)]
            },
            'FullPositionVector': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DDateTime',
                    'name': 'utcTime',
                    'optional': True
                }, {
                    'type': 'Longitude',
                    'name': 'long'
                }, {
                    'type': 'Latitude',
                    'name': 'lat'
                }, {
                    'type': 'Elevation',
                    'name': 'elevation',
                    'optional': True
                }, {
                    'type': 'Heading',
                    'name': 'heading',
                    'optional': True
                }, {
                    'type': 'TransmissionAndSpeed',
                    'name': 'speed',
                    'optional': True
                }, {
                    'type': 'PositionalAccuracy',
                    'name': 'posAccuracy',
                    'optional': True
                }, {
                    'type': 'TimeConfidence',
                    'name': 'timeConfidence',
                    'optional': True
                }, {
                    'type': 'PositionConfidenceSet',
                    'name': 'posConfidence',
                    'optional': True
                }, {
                    'type': 'SpeedandHeadingandThrottleConfidence',
                    'name': 'speedConfidence',
                    'optional': True
                }, None]
            },
            'GenericLane': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'LaneID',
                    'name': 'laneID'
                }, {
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'ApproachID',
                    'name': 'ingressApproach',
                    'optional': True
                }, {
                    'type': 'ApproachID',
                    'name': 'egressApproach',
                    'optional': True
                }, {
                    'type': 'LaneAttributes',
                    'name': 'laneAttributes'
                }, {
                    'type': 'AllowedManeuvers',
                    'name': 'maneuvers',
                    'optional': True
                }, {
                    'type': 'NodeListXY',
                    'name': 'nodeList'
                }, {
                    'type': 'ConnectsToList',
                    'name': 'connectsTo',
                    'optional': True
                }, {
                    'type': 'OverlayLaneList',
                    'name': 'overlays',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'IntersectionAccessPoint': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'LaneID',
                    'name': 'lane'
                }, {
                    'type': 'ApproachID',
                    'name': 'approach'
                }, {
                    'type': 'LaneConnectionID',
                    'name': 'connection'
                }, None]
            },
            'IntersectionGeometry': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'IntersectionReferenceID',
                    'name': 'id'
                }, {
                    'type': 'MsgCount',
                    'name': 'revision'
                }, {
                    'type': 'Position3D',
                    'name': 'refPoint'
                }, {
                    'type': 'LaneWidth',
                    'name': 'laneWidth',
                    'optional': True
                }, {
                    'type': 'SpeedLimitList',
                    'name': 'speedLimits',
                    'optional': True
                }, {
                    'type': 'LaneList',
                    'name': 'laneSet'
                }, {
                    'type': 'PreemptPriorityList',
                    'name': 'preemptPriorityData',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'IntersectionGeometryList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'IntersectionGeometry'
                },
                'size': [(1, 32)]
            },
            'IntersectionReferenceID': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'RoadRegulatorID',
                    'name': 'region',
                    'optional': True
                }, {
                    'type': 'IntersectionID',
                    'name': 'id'
                }]
            },
            'IntersectionState': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'IntersectionReferenceID',
                    'name': 'id'
                }, {
                    'type': 'MsgCount',
                    'name': 'revision'
                }, {
                    'type': 'IntersectionStatusObject',
                    'name': 'status'
                }, {
                    'type': 'MinuteOfTheYear',
                    'name': 'moy',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'timeStamp',
                    'optional': True
                }, {
                    'type': 'EnabledLaneList',
                    'name': 'enabledLanes',
                    'optional': True
                }, {
                    'type': 'MovementList',
                    'name': 'states'
                }, {
                    'type': 'ManeuverAssistList',
                    'name': 'maneuverAssistList',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'IntersectionStateList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'IntersectionState'
                },
                'size': [(1, 32)]
            },
            'LaneAttributes': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'LaneDirection',
                    'name': 'directionalUse'
                }, {
                    'type': 'LaneSharing',
                    'name': 'sharedWith'
                }, {
                    'type': 'LaneTypeAttributes',
                    'name': 'laneType'
                }, {
                    'type': 'RegionalExtension',
                    'actual-parameters': ['{'],
                    'name': 'regional',
                    'optional': True
                }]
            },
            'LaneDataAttribute': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'DeltaAngle',
                    'name': 'pathEndPointAngle'
                }, {
                    'type': 'RoadwayCrownAngle',
                    'name': 'laneCrownPointCenter'
                }, {
                    'type': 'RoadwayCrownAngle',
                    'name': 'laneCrownPointLeft'
                }, {
                    'type': 'RoadwayCrownAngle',
                    'name': 'laneCrownPointRight'
                }, {
                    'type': 'MergeDivergeNodeAngle',
                    'name': 'laneAngle'
                }, {
                    'type': 'SpeedLimitList',
                    'name': 'speedLimits'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional'
                }, None]
            },
            'LaneDataAttributeList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'LaneDataAttribute'
                },
                'size': [(1, 8)]
            },
            'LaneList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'GenericLane'
                },
                'size': [(1, 255)]
            },
            'LaneSharing': {
                'type':
                'BIT STRING',
                'named-bits': [('overlappingLaneDescriptionProvided', '0'),
                               ('multipleLanesTreatedAsOneLane', '1'),
                               ('otherNonMotorizedTrafficTypes', '2'),
                               ('individualMotorizedVehicleTraffic', '3'),
                               ('busVehicleTraffic', '4'),
                               ('taxiVehicleTraffic', '5'),
                               ('pedestriansTraffic', '6'),
                               ('cyclistVehicleTraffic', '7'),
                               ('trackedVehicleTraffic', '8'),
                               ('pedestrianTraffic', '9')],
                'size': [10]
            },
            'LaneTypeAttributes': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'LaneAttributes-Vehicle',
                    'name': 'vehicle'
                }, {
                    'type': 'LaneAttributes-Crosswalk',
                    'name': 'crosswalk'
                }, {
                    'type': 'LaneAttributes-Bike',
                    'name': 'bikeLane'
                }, {
                    'type': 'LaneAttributes-Sidewalk',
                    'name': 'sidewalk'
                }, {
                    'type': 'LaneAttributes-Barrier',
                    'name': 'median'
                }, {
                    'type': 'LaneAttributes-Striping',
                    'name': 'striping'
                }, {
                    'type': 'LaneAttributes-TrackedVehicle',
                    'name': 'trackedVehicle'
                }, {
                    'type': 'LaneAttributes-Parking',
                    'name': 'parking'
                }, None]
            },
            'ManeuverAssistList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'ConnectionManeuverAssist'
                },
                'size': [(1, 16)]
            },
            'MovementEvent': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MovementPhaseState',
                    'name': 'eventState'
                }, {
                    'type': 'TimeChangeDetails',
                    'name': 'timing',
                    'optional': True
                }, {
                    'type': 'AdvisorySpeedList',
                    'name': 'speeds',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'MovementEventList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'MovementEvent'
                },
                'size': [(1, 16)]
            },
            'MovementList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'MovementState'
                },
                'size': [(1, 255)]
            },
            'MovementState': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DescriptiveName',
                    'name': 'movementName',
                    'optional': True
                }, {
                    'type': 'SignalGroupID',
                    'name': 'signalGroup'
                }, {
                    'type': 'MovementEventList',
                    'name': 'state-time-speed'
                }, {
                    'type': 'ManeuverAssistList',
                    'name': 'maneuverAssistList',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'NodeAttributeSetXY': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'NodeAttributeXYList',
                    'name': 'localNode',
                    'optional': True
                }, {
                    'type': 'SegmentAttributeXYList',
                    'name': 'disabled',
                    'optional': True
                }, {
                    'type': 'SegmentAttributeXYList',
                    'name': 'enabled',
                    'optional': True
                }, {
                    'type': 'LaneDataAttributeList',
                    'name': 'data',
                    'optional': True
                }, {
                    'type': 'Offset-B10',
                    'name': 'dWidth',
                    'optional': True
                }, {
                    'type': 'Offset-B10',
                    'name': 'dElevation',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'NodeAttributeXY': {
                'type':
                'ENUMERATED',
                'values': [('reserved', 0), ('stopLine', 1),
                           ('roundedCapStyleA', 2), ('roundedCapStyleB', 3),
                           ('mergePoint', 4), ('divergePoint', 5),
                           ('downstreamStopLine', 6),
                           ('downstreamStartNode', 7), ('closedToTraffic', 8),
                           ('safeIsland', 9), ('curbPresentAtStepOff', 10),
                           ('hydrantPresent', 11), None]
            },
            'NodeAttributeXYList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'NodeAttributeXY'
                },
                'size': [(1, 8)]
            },
            'Node-LLmD-64b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Longitude',
                    'name': 'lon'
                }, {
                    'type': 'Latitude',
                    'name': 'lat'
                }]
            },
            'Node-XY-20b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B10',
                    'name': 'x'
                }, {
                    'type': 'Offset-B10',
                    'name': 'y'
                }]
            },
            'Node-XY-22b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B11',
                    'name': 'x'
                }, {
                    'type': 'Offset-B11',
                    'name': 'y'
                }]
            },
            'Node-XY-24b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B12',
                    'name': 'x'
                }, {
                    'type': 'Offset-B12',
                    'name': 'y'
                }]
            },
            'Node-XY-26b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B13',
                    'name': 'x'
                }, {
                    'type': 'Offset-B13',
                    'name': 'y'
                }]
            },
            'Node-XY-28b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B14',
                    'name': 'x'
                }, {
                    'type': 'Offset-B14',
                    'name': 'y'
                }]
            },
            'Node-XY-32b': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Offset-B16',
                    'name': 'x'
                }, {
                    'type': 'Offset-B16',
                    'name': 'y'
                }]
            },
            'NodeListXY': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'NodeSetXY',
                    'name': 'nodes'
                }, {
                    'type': 'ComputedLane',
                    'name': 'computed'
                }, None]
            },
            'NodeOffsetPointXY': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'Node-XY-20b',
                    'name': 'node-XY1'
                }, {
                    'type': 'Node-XY-22b',
                    'name': 'node-XY2'
                }, {
                    'type': 'Node-XY-24b',
                    'name': 'node-XY3'
                }, {
                    'type': 'Node-XY-26b',
                    'name': 'node-XY4'
                }, {
                    'type': 'Node-XY-28b',
                    'name': 'node-XY5'
                }, {
                    'type': 'Node-XY-32b',
                    'name': 'node-XY6'
                }, {
                    'type': 'Node-LLmD-64b',
                    'name': 'node-LatLon'
                }, {
                    'type': 'RegionalExtension',
                    'actual-parameters': ['{'],
                    'name': 'regional'
                }]
            },
            'NodeXY': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'NodeOffsetPointXY',
                    'name': 'delta'
                }, {
                    'type': 'NodeAttributeSetXY',
                    'name': 'attributes',
                    'optional': True
                }, None]
            },
            'NodeSetXY': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'NodeXY'
                },
                'size': [(2, 63)]
            },
            'OverlayLaneList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'LaneID'
                },
                'size': [(1, 5)]
            },
            'PositionalAccuracy': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'SemiMajorAxisAccuracy',
                    'name': 'semiMajor'
                }, {
                    'type': 'SemiMinorAxisAccuracy',
                    'name': 'semiMinor'
                }, {
                    'type': 'SemiMajorAxisOrientation',
                    'name': 'orientation'
                }]
            },
            'PositionConfidenceSet': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'PositionConfidence',
                    'name': 'pos'
                }, {
                    'type': 'ElevationConfidence',
                    'name': 'elevation'
                }]
            },
            'Position3D': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Latitude',
                    'name': 'lat'
                }, {
                    'type': 'Longitude',
                    'name': 'long'
                }, {
                    'type': 'Elevation',
                    'name': 'elevation',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'PreemptPriorityList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'SignalControlZone'
                },
                'size': [(1, 32)]
            },
            'RegulatorySpeedLimit': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'SpeedLimitType',
                    'name': 'type'
                }, {
                    'type': 'Velocity',
                    'name': 'speed'
                }]
            },
            'RequestorDescription': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'VehicleID',
                    'name': 'id'
                }, {
                    'type': 'RequestorType',
                    'name': 'type',
                    'optional': True
                }, {
                    'type': 'RequestorPositionVector',
                    'name': 'position',
                    'optional': True
                }, {
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'DescriptiveName',
                    'name': 'routeName',
                    'optional': True
                }, {
                    'type': 'TransitVehicleStatus',
                    'name': 'transitStatus',
                    'optional': True
                }, {
                    'type': 'TransitVehicleOccupancy',
                    'name': 'transitOccupancy',
                    'optional': True
                }, {
                    'type': 'DeltaTime',
                    'name': 'transitSchedule',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'RequestorPositionVector': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'Position3D',
                    'name': 'position'
                }, {
                    'type': 'Angle',
                    'name': 'heading',
                    'optional': True
                }, {
                    'type': 'TransmissionAndSpeed',
                    'name': 'speed',
                    'optional': True
                }, None]
            },
            'RequestorType': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'BasicVehicleRole',
                    'name': 'role'
                }, {
                    'type': 'RequestSubRole',
                    'name': 'subrole',
                    'optional': True
                }, {
                    'type': 'RequestImportanceLevel',
                    'name': 'request',
                    'optional': True
                }, {
                    'type': 'Iso3833VehicleType',
                    'name': 'iso3883',
                    'optional': True
                }, {
                    'type': 'VehicleType',
                    'name': 'hpmsType',
                    'optional': True
                }, {
                    'type': 'RegionalExtension',
                    'actual-parameters': ['{'],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'RestrictionClassAssignment': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'RestrictionClassID',
                    'name': 'id'
                }, {
                    'type': 'RestrictionUserTypeList',
                    'name': 'users'
                }]
            },
            'RestrictionClassList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'RestrictionClassAssignment'
                },
                'size': [(1, 254)]
            },
            'RestrictionUserType': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'RestrictionAppliesTo',
                    'name': 'basicType'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional'
                }, None]
            },
            'RestrictionUserTypeList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'RestrictionUserType'
                },
                'size': [(1, 16)]
            },
            'RoadLaneSetList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'GenericLane'
                },
                'size': [(1, 255)]
            },
            'RoadSegmentReferenceID': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'RoadRegulatorID',
                    'name': 'region',
                    'optional': True
                }, {
                    'type': 'RoadSegmentID',
                    'name': 'id'
                }]
            },
            'RoadSegment': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'DescriptiveName',
                    'name': 'name',
                    'optional': True
                }, {
                    'type': 'RoadSegmentReferenceID',
                    'name': 'id'
                }, {
                    'type': 'MsgCount',
                    'name': 'revision'
                }, {
                    'type': 'Position3D',
                    'name': 'refPoint'
                }, {
                    'type': 'LaneWidth',
                    'name': 'laneWidth',
                    'optional': True
                }, {
                    'type': 'SpeedLimitList',
                    'name': 'speedLimits',
                    'optional': True
                }, {
                    'type': 'RoadLaneSetList',
                    'name': 'roadLaneSet'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'RoadSegmentList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'RoadSegment'
                },
                'size': [(1, 32)]
            },
            'RTCMheader': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'GNSSstatus',
                    'name': 'status'
                }, {
                    'type': 'AntennaOffsetSet',
                    'name': 'offsetSet'
                }]
            },
            'RTCMmessageList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'RTCMmessage'
                },
                'size': [(1, 5)]
            },
            'SegmentAttributeXYList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'SegmentAttributeXY'
                },
                'size': [(1, 8)]
            },
            'SignalControlZone': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'RegionalExtension',
                    'actual-parameters': ['{'],
                    'name': 'zone'
                }, None]
            },
            'SignalRequesterInfo': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'VehicleID',
                    'name': 'id'
                }, {
                    'type': 'RequestID',
                    'name': 'request'
                }, {
                    'type': 'MsgCount',
                    'name': 'sequenceNumber'
                }, {
                    'type': 'BasicVehicleRole',
                    'name': 'role',
                    'optional': True
                }, {
                    'type': 'RequestorType',
                    'name': 'typeData',
                    'optional': True
                }, None]
            },
            'SignalRequest': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'IntersectionReferenceID',
                    'name': 'id'
                }, {
                    'type': 'RequestID',
                    'name': 'requestID'
                }, {
                    'type': 'PriorityRequestType',
                    'name': 'requestType'
                }, {
                    'type': 'IntersectionAccessPoint',
                    'name': 'inBoundLane'
                }, {
                    'type': 'IntersectionAccessPoint',
                    'name': 'outBoundLane',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SignalRequestList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'SignalRequestPackage'
                },
                'size': [(1, 32)]
            },
            'SignalRequestPackage': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'SignalRequest',
                    'name': 'request'
                }, {
                    'type': 'MinuteOfTheYear',
                    'name': 'minute',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'second',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'duration',
                    'optional': True
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SignalStatus': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'MsgCount',
                    'name': 'sequenceNumber'
                }, {
                    'type': 'IntersectionReferenceID',
                    'name': 'id'
                }, {
                    'type': 'SignalStatusPackageList',
                    'name': 'sigStatus'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SignalStatusList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'SignalStatus'
                },
                'size': [(1, 32)]
            },
            'SignalStatusPackageList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'SignalStatusPackage'
                },
                'size': [(1, 32)]
            },
            'SignalStatusPackage': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'SignalRequesterInfo',
                    'name': 'requester',
                    'optional': True
                }, {
                    'type': 'IntersectionAccessPoint',
                    'name': 'inboundOn'
                }, {
                    'type': 'IntersectionAccessPoint',
                    'name': 'outboundOn',
                    'optional': True
                }, {
                    'type': 'MinuteOfTheYear',
                    'name': 'minute',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'second',
                    'optional': True
                }, {
                    'type': 'DSecond',
                    'name': 'duration',
                    'optional': True
                }, {
                    'type': 'PrioritizationResponseStatus',
                    'name': 'status'
                }, {
                    'type': 'SEQUENCE OF',
                    'element': {
                        'type': 'RegionalExtension',
                        'actual-parameters': ['{']
                    },
                    'size': [(1, 4)],
                    'name': 'regional',
                    'optional': True
                }, None]
            },
            'SpeedandHeadingandThrottleConfidence': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'HeadingConfidence',
                    'name': 'heading'
                }, {
                    'type': 'SpeedConfidence',
                    'name': 'speed'
                }, {
                    'type': 'ThrottleConfidence',
                    'name': 'throttle'
                }]
            },
            'SpeedLimitList': {
                'type': 'SEQUENCE OF',
                'element': {
                    'type': 'RegulatorySpeedLimit'
                },
                'size': [(1, 9)]
            },
            'SpeedLimitType': {
                'type':
                'ENUMERATED',
                'values': [('unknown', 0), ('maxSpeedInSchoolZone', 1),
                           ('maxSpeedInSchoolZoneWhenChildrenArePresent', 2),
                           ('maxSpeedInConstructionZone', 3),
                           ('vehicleMinSpeed', 4), ('vehicleMaxSpeed', 5),
                           ('vehicleNightMaxSpeed', 6), ('truckMinSpeed', 7),
                           ('truckMaxSpeed', 8), ('truckNightMaxSpeed', 9),
                           ('vehiclesWithTrailersMinSpeed', 10),
                           ('vehiclesWithTrailersMaxSpeed', 11),
                           ('vehiclesWithTrailersNightMaxSpeed', 12), None]
            },
            'TimeChangeDetails': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'TimeMark',
                    'name': 'startTime',
                    'optional': True
                }, {
                    'type': 'TimeMark',
                    'name': 'minEndTime'
                }, {
                    'type': 'TimeMark',
                    'name': 'maxEndTime',
                    'optional': True
                }, {
                    'type': 'TimeMark',
                    'name': 'likelyTime',
                    'optional': True
                }, {
                    'type': 'TimeIntervalConfidence',
                    'name': 'confidence',
                    'optional': True
                }, {
                    'type': 'TimeMark',
                    'name': 'nextTime',
                    'optional': True
                }]
            },
            'TimeMark': {
                'type': 'INTEGER',
                'restricted-to': [(0, 36001)]
            },
            'TransmissionAndSpeed': {
                'type':
                'SEQUENCE',
                'members': [{
                    'type': 'TransmissionState',
                    'name': 'transmisson'
                }, {
                    'type': 'Velocity',
                    'name': 'speed'
                }]
            },
            'VehicleID': {
                'type':
                'CHOICE',
                'members': [{
                    'type': 'TemporaryID',
                    'name': 'entityID'
                }, {
                    'type': 'StationID',
                    'name': 'stationID'
                }]
            },
            'AdvisorySpeedType': {
                'type':
                'ENUMERATED',
                'values': [('none', 0), ('greenwave', 1), ('ecoDrive', 2),
                           ('transit', 3), None]
            },
            'AllowedManeuvers': {
                'type':
                'BIT STRING',
                'named-bits': [('maneuverStraightAllowed', '0'),
                               ('maneuverLeftAllowed', '1'),
                               ('maneuverRightAllowed', '2'),
                               ('maneuverUTurnAllowed', '3'),
                               ('maneuverLeftTurnOnRedAllowed', '4'),
                               ('maneuverRightTurnOnRedAllowed', '5'),
                               ('maneuverLaneChangeAllowed', '6'),
                               ('maneuverNoStoppingAllowed', '7'),
                               ('yieldAllwaysRequired', '8'),
                               ('goWithHalt', '9'), ('caution', '10'),
                               ('reserved1', '11')],
                'size': [12]
            },
            'Angle': {
                'type': 'INTEGER',
                'restricted-to': [(0, 28800)]
            },
            'ApproachID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 15)]
            },
            'BasicVehicleRole': {
                'type':
                'ENUMERATED',
                'values':
                [('basicVehicle', 0), ('publicTransport', 1),
                 ('specialTransport', 2),
                 ('dangerousGoods', 3), ('roadWork', 4), ('roadRescue', 5),
                 ('emergency', 6), ('safetyCar', 7), ('none-unknown', 8),
                 ('truck', 9), ('motorcycle', 10), ('roadSideSource', 11),
                 ('police', 12), ('fire', 13), ('ambulance', 14), ('dot', 15),
                 ('transit', 16), ('slowMoving', 17), ('stopNgo', 18),
                 ('cyclist', 19), ('pedestrian', 20), ('nonMotorized', 21),
                 ('military', 22), None]
            },
            'DDay': {
                'type': 'INTEGER',
                'restricted-to': [(0, 31)]
            },
            'DeltaAngle': {
                'type': 'INTEGER',
                'restricted-to': [(-150, 150)]
            },
            'DeltaTime': {
                'type': 'INTEGER',
                'restricted-to': [(-122, 121)]
            },
            'DescriptiveName': {
                'type': 'IA5String',
                'size': [(1, 63)]
            },
            'DHour': {
                'type': 'INTEGER',
                'restricted-to': [(0, 31)]
            },
            'DMinute': {
                'type': 'INTEGER',
                'restricted-to': [(0, 60)]
            },
            'DMonth': {
                'type': 'INTEGER',
                'restricted-to': [(0, 12)]
            },
            'DOffset': {
                'type': 'INTEGER',
                'restricted-to': [(-840, 840)]
            },
            'DrivenLineOffsetLg': {
                'type': 'INTEGER',
                'restricted-to': [(-32767, 32767)]
            },
            'DrivenLineOffsetSm': {
                'type': 'INTEGER',
                'restricted-to': [(-2047, 2047)]
            },
            'DSecond': {
                'type': 'INTEGER',
                'restricted-to': [(0, 65535)]
            },
            'DSRCmsgID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 32767)]
            },
            'DYear': {
                'type': 'INTEGER',
                'restricted-to': [(0, 4095)]
            },
            'Elevation': {
                'type': 'INTEGER',
                'restricted-to': [(-4096, 61439)]
            },
            'ElevationConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('elev-500-00', 1),
                           ('elev-200-00', 2), ('elev-100-00', 3),
                           ('elev-050-00', 4), ('elev-020-00', 5),
                           ('elev-010-00', 6), ('elev-005-00', 7),
                           ('elev-002-00', 8), ('elev-001-00', 9),
                           ('elev-000-50', 10), ('elev-000-20', 11),
                           ('elev-000-10', 12), ('elev-000-05', 13),
                           ('elev-000-02', 14), ('elev-000-01', 15)]
            },
            'FuelType': {
                'type': 'INTEGER',
                'restricted-to': [(0, 15)]
            },
            'GNSSstatus': {
                'type':
                'BIT STRING',
                'named-bits': [('unavailable', '0'), ('isHealthy', '1'),
                               ('isMonitored', '2'), ('baseStationType', '3'),
                               ('aPDOPofUnder5', '4'), ('inViewOfUnder5', '5'),
                               ('localCorrectionsPresent', '6'),
                               ('networkCorrectionsPresent', '7')],
                'size': [8]
            },
            'HeadingConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('prec10deg', 1),
                           ('prec05deg', 2), ('prec01deg', 3),
                           ('prec0-1deg', 4), ('prec0-05deg', 5),
                           ('prec0-01deg', 6), ('prec0-0125deg', 7)]
            },
            'Heading': {
                'type': 'INTEGER',
                'restricted-to': [(0, 28800)]
            },
            'IntersectionID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 65535)]
            },
            'IntersectionStatusObject': {
                'type':
                'BIT STRING',
                'named-bits': [('manualControlIsEnabled', '0'),
                               ('stopTimeIsActivated', '1'),
                               ('failureFlash', '2'), ('preemptIsActive', '3'),
                               ('signalPriorityIsActive', '4'),
                               ('fixedTimeOperation', '5'),
                               ('trafficDependentOperation', '6'),
                               ('standbyOperation', '7'), ('failureMode', '8'),
                               ('off', '9'), ('recentMAPmessageUpdate', '10'),
                               ('recentChangeInMAPassignedLanesIDsUsed', '11'),
                               ('noValidMAPisAvailableAtThisTime', '12'),
                               ('noValidSPATisAvailableAtThisTime', '13')],
                'size': [16]
            },
            'LaneAttributes-Barrier': {
                'type':
                'BIT STRING',
                'named-bits': [('median-RevocableLane', '0'), ('median', '1'),
                               ('whiteLineHashing', '2'),
                               ('stripedLines', '3'),
                               ('doubleStripedLines', '4'),
                               ('trafficCones', '5'),
                               ('constructionBarrier', '6'),
                               ('trafficChannels', '7'), ('lowCurbs', '8'),
                               ('highCurbs', '9')],
                'size': [16]
            },
            'LaneAttributes-Bike': {
                'type':
                'BIT STRING',
                'named-bits': [('bikeRevocableLane', '0'),
                               ('pedestrianUseAllowed', '1'),
                               ('isBikeFlyOverLane', '2'),
                               ('fixedCycleTime', '3'),
                               ('biDirectionalCycleTimes', '4'),
                               ('isolatedByBarrier', '5'),
                               ('unsignalizedSegmentsPresent', '6')],
                'size': [16]
            },
            'LaneAttributes-Crosswalk': {
                'type':
                'BIT STRING',
                'named-bits': [('crosswalkRevocableLane', '0'),
                               ('bicyleUseAllowed', '1'),
                               ('isXwalkFlyOverLane', '2'),
                               ('fixedCycleTime', '3'),
                               ('biDirectionalCycleTimes', '4'),
                               ('hasPushToWalkButton', '5'),
                               ('audioSupport', '6'),
                               ('rfSignalRequestPresent', '7'),
                               ('unsignalizedSegmentsPresent', '8')],
                'size': [16]
            },
            'LaneAttributes-Parking': {
                'type':
                'BIT STRING',
                'named-bits': [('parkingRevocableLane', '0'),
                               ('parallelParkingInUse', '1'),
                               ('headInParkingInUse', '2'),
                               ('doNotParkZone', '3'),
                               ('parkingForBusUse', '4'),
                               ('parkingForTaxiUse', '5'),
                               ('noPublicParkingUse', '6')],
                'size': [16]
            },
            'LaneAttributes-Sidewalk': {
                'type':
                'BIT STRING',
                'named-bits': [('sidewalk-RevocableLane', '0'),
                               ('bicyleUseAllowed', '1'),
                               ('isSidewalkFlyOverLane', '2'),
                               ('walkBikes', '3')],
                'size': [16]
            },
            'LaneAttributes-Striping': {
                'type':
                'BIT STRING',
                'named-bits': [('stripeToConnectingLanesRevocableLane', '0'),
                               ('stripeDrawOnLeft', '1'),
                               ('stripeDrawOnRight', '2'),
                               ('stripeToConnectingLanesLeft', '3'),
                               ('stripeToConnectingLanesRight', '4'),
                               ('stripeToConnectingLanesAhead', '5')],
                'size': [16]
            },
            'LaneAttributes-TrackedVehicle': {
                'type':
                'BIT STRING',
                'named-bits': [('spec-RevocableLane', '0'),
                               ('spec-commuterRailRoadTrack', '1'),
                               ('spec-lightRailRoadTrack', '2'),
                               ('spec-heavyRailRoadTrack', '3'),
                               ('spec-otherRailType', '4')],
                'size': [16]
            },
            'LaneAttributes-Vehicle': {
                'type':
                'BIT STRING',
                'named-bits': [('isVehicleRevocableLane', '0'),
                               ('isVehicleFlyOverLane', '1'),
                               ('hovLaneUseOnly', '2'),
                               ('restrictedToBusUse', '3'),
                               ('restrictedToTaxiUse', '4'),
                               ('restrictedFromPublicUse', '5'),
                               ('hasIRbeaconCoverage', '6'),
                               ('permissionOnRequest', '7')],
                'size': [8, None]
            },
            'LaneConnectionID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'LaneDirection': {
                'type': 'BIT STRING',
                'named-bits': [('ingressPath', '0'), ('egressPath', '1')],
                'size': [2]
            },
            'LaneID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'LayerID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 100)]
            },
            'LayerType': {
                'type':
                'ENUMERATED',
                'values': [('none', 0), ('mixedContent', 1),
                           ('generalMapData', 2), ('intersectionData', 3),
                           ('curveData', 4), ('roadwaySectionData', 5),
                           ('parkingAreaData', 6), ('sharedLaneData', 7), None]
            },
            'LaneWidth': {
                'type': 'INTEGER',
                'restricted-to': [(0, 32767)]
            },
            'MergeDivergeNodeAngle': {
                'type': 'INTEGER',
                'restricted-to': [(-180, 180)]
            },
            'MinuteOfTheYear': {
                'type': 'INTEGER',
                'restricted-to': [(0, 527040)]
            },
            'MovementPhaseState': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('dark', 1),
                           ('stop-Then-Proceed', 2), ('stop-And-Remain', 3),
                           ('pre-Movement', 4),
                           ('permissive-Movement-Allowed', 5),
                           ('protected-Movement-Allowed', 6),
                           ('permissive-clearance', 7),
                           ('protected-clearance', 8),
                           ('caution-Conflicting-Traffic', 9)]
            },
            'MsgCount': {
                'type': 'INTEGER',
                'restricted-to': [(0, 127)]
            },
            'Offset-B09': {
                'type': 'INTEGER',
                'restricted-to': [(-256, 255)]
            },
            'Offset-B10': {
                'type': 'INTEGER',
                'restricted-to': [(-512, 511)]
            },
            'Offset-B11': {
                'type': 'INTEGER',
                'restricted-to': [(-1024, 1023)]
            },
            'Offset-B12': {
                'type': 'INTEGER',
                'restricted-to': [(-2048, 2047)]
            },
            'Offset-B13': {
                'type': 'INTEGER',
                'restricted-to': [(-4096, 4095)]
            },
            'Offset-B14': {
                'type': 'INTEGER',
                'restricted-to': [(-8192, 8191)]
            },
            'Offset-B16': {
                'type': 'INTEGER',
                'restricted-to': [(-32768, 32767)]
            },
            'PedestrianBicycleDetect': {
                'type': 'BOOLEAN'
            },
            'PositionConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('a500m', 1), ('a200m', 2),
                           ('a100m', 3), ('a50m', 4), ('a20m', 5), ('a10m', 6),
                           ('a5m', 7), ('a2m', 8), ('a1m', 9), ('a50cm', 10),
                           ('a20cm', 11), ('a10cm', 12), ('a5cm', 13),
                           ('a2cm', 14), ('a1cm', 15)]
            },
            'PrioritizationResponseStatus': {
                'type':
                'ENUMERATED',
                'values': [('unknown', 0), ('requested', 1), ('processing', 2),
                           ('watchOtherTraffic', 3), ('granted', 4),
                           ('rejected', 5), ('maxPresence', 6),
                           ('reserviceLocked', 7), None]
            },
            'PriorityRequestType': {
                'type':
                'ENUMERATED',
                'values': [('priorityRequestTypeReserved', 0),
                           ('priorityRequest', 1),
                           ('priorityRequestUpdate', 2),
                           ('priorityCancellation', 3), None]
            },
            'RegionId': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'RequestID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'RequestImportanceLevel': {
                'type':
                'ENUMERATED',
                'values': [('requestImportanceLevelUnKnown', 0),
                           ('requestImportanceLevel1', 1),
                           ('requestImportanceLevel2', 2),
                           ('requestImportanceLevel3', 3),
                           ('requestImportanceLevel4', 4),
                           ('requestImportanceLevel5', 5),
                           ('requestImportanceLevel6', 6),
                           ('requestImportanceLevel7', 7),
                           ('requestImportanceLevel8', 8),
                           ('requestImportanceLevel9', 9),
                           ('requestImportanceLevel10', 10),
                           ('requestImportanceLevel11', 11),
                           ('requestImportanceLevel12', 12),
                           ('requestImportanceLevel13', 13),
                           ('requestImportanceLevel14', 14),
                           ('requestImportanceReserved', 15)]
            },
            'RequestSubRole': {
                'type':
                'ENUMERATED',
                'values': [('requestSubRoleUnKnown', 0),
                           ('requestSubRole1', 1), ('requestSubRole2', 2),
                           ('requestSubRole3', 3), ('requestSubRole4', 4),
                           ('requestSubRole5', 5), ('requestSubRole6', 6),
                           ('requestSubRole7', 7), ('requestSubRole8', 8),
                           ('requestSubRole9', 9), ('requestSubRole10', 10),
                           ('requestSubRole11', 11), ('requestSubRole12', 12),
                           ('requestSubRole13', 13), ('requestSubRole14', 14),
                           ('requestSubRoleReserved', 15)]
            },
            'RestrictionAppliesTo': {
                'type':
                'ENUMERATED',
                'values': [('none', 0), ('equippedTransit', 1),
                           ('equippedTaxis', 2), ('equippedOther', 3),
                           ('emissionCompliant', 4), ('equippedBicycle', 5),
                           ('weightCompliant', 6), ('heightCompliant', 7),
                           ('pedestrians', 8), ('slowMovingPersons', 9),
                           ('wheelchairUsers', 10), ('visualDisabilities', 11),
                           ('audioDisabilities', 12),
                           ('otherUnknownDisabilities', 13), None]
            },
            'RestrictionClassID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'RoadRegulatorID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 65535)]
            },
            'RoadSegmentID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 65535)]
            },
            'RoadwayCrownAngle': {
                'type': 'INTEGER',
                'restricted-to': [(-128, 127)]
            },
            'RTCMmessage': {
                'type': 'OCTET STRING',
                'size': [(1, 1023)]
            },
            'RTCM-Revision': {
                'type':
                'ENUMERATED',
                'values': [('unknown', 0), ('rtcmRev2', 1), ('rtcmRev3', 2),
                           ('reserved', 3), None]
            },
            'Scale-B12': {
                'type': 'INTEGER',
                'restricted-to': [(-2048, 2047)]
            },
            'SignalGroupID': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'SegmentAttributeXY': {
                'type':
                'ENUMERATED',
                'values': [
                    ('reserved', 0), ('doNotBlock', 1), ('whiteLine', 2),
                    ('mergingLaneLeft', 3), ('mergingLaneRight', 4),
                    ('curbOnLeft', 5), ('curbOnRight', 6),
                    ('loadingzoneOnLeft', 7), ('loadingzoneOnRight', 8),
                    ('turnOutPointOnLeft', 9), ('turnOutPointOnRight', 10),
                    ('adjacentParkingOnLeft', 11),
                    ('adjacentParkingOnRight', 12),
                    ('adjacentBikeLaneOnLeft', 13),
                    ('adjacentBikeLaneOnRight', 14), ('sharedBikeLane', 15),
                    ('bikeBoxInFront', 16), ('transitStopOnLeft', 17),
                    ('transitStopOnRight', 18), ('transitStopInLane', 19),
                    ('sharedWithTrackedVehicle', 20), ('safeIsland', 21),
                    ('lowCurbsPresent', 22), ('rumbleStripPresent', 23),
                    ('audibleSignalingPresent', 24),
                    ('adaptiveTimingPresent', 25),
                    ('rfSignalRequestPresent', 26),
                    ('partialCurbIntrusion', 27), ('taperToLeft', 28),
                    ('taperToRight', 29), ('taperToCenterLine', 30),
                    ('parallelParking', 31), ('headInParking', 32),
                    ('freeParking', 33), ('timeRestrictionsOnParking', 34),
                    ('costToPark', 35), ('midBlockCurbPresent', 36),
                    ('unEvenPavementPresent', 37), None
                ]
            },
            'SemiMajorAxisAccuracy': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'SemiMajorAxisOrientation': {
                'type': 'INTEGER',
                'restricted-to': [(0, 65535)]
            },
            'SemiMinorAxisAccuracy': {
                'type': 'INTEGER',
                'restricted-to': [(0, 255)]
            },
            'SpeedAdvice': {
                'type': 'INTEGER',
                'restricted-to': [(0, 500)]
            },
            'SpeedConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('prec100ms', 1),
                           ('prec10ms', 2), ('prec5ms', 3), ('prec1ms', 4),
                           ('prec0-1ms', 5), ('prec0-05ms', 6),
                           ('prec0-01ms', 7)]
            },
            'TemporaryID': {
                'type': 'OCTET STRING',
                'size': [4]
            },
            'ThrottleConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('prec10percent', 1),
                           ('prec1percent', 2), ('prec0-5percent', 3)]
            },
            'TimeConfidence': {
                'type':
                'ENUMERATED',
                'values': [('unavailable', 0), ('time-100-000', 1),
                           ('time-050-000', 2), ('time-020-000', 3),
                           ('time-010-000', 4), ('time-002-000', 5),
                           ('time-001-000', 6), ('time-000-500', 7),
                           ('time-000-200', 8), ('time-000-100', 9),
                           ('time-000-050', 10), ('time-000-020', 11),
                           ('time-000-010', 12), ('time-000-005', 13),
                           ('time-000-002', 14), ('time-000-001', 15),
                           ('time-000-000-5', 16), ('time-000-000-2', 17),
                           ('time-000-000-1', 18), ('time-000-000-05', 19),
                           ('time-000-000-02', 20), ('time-000-000-01', 21),
                           ('time-000-000-005', 22), ('time-000-000-002', 23),
                           ('time-000-000-001', 24),
                           ('time-000-000-000-5', 25),
                           ('time-000-000-000-2', 26),
                           ('time-000-000-000-1', 27),
                           ('time-000-000-000-05', 28),
                           ('time-000-000-000-02', 29),
                           ('time-000-000-000-01', 30),
                           ('time-000-000-000-005', 31),
                           ('time-000-000-000-002', 32),
                           ('time-000-000-000-001', 33),
                           ('time-000-000-000-000-5', 34),
                           ('time-000-000-000-000-2', 35),
                           ('time-000-000-000-000-1', 36),
                           ('time-000-000-000-000-05', 37),
                           ('time-000-000-000-000-02', 38),
                           ('time-000-000-000-000-01', 39)]
            },
            'TimeIntervalConfidence': {
                'type': 'INTEGER',
                'restricted-to': [(0, 15)]
            },
            'TransitVehicleOccupancy': {
                'type':
                'ENUMERATED',
                'values': [('occupancyUnknown', 0), ('occupancyEmpty', 1),
                           ('occupancyVeryLow', 2), ('occupancyLow', 3),
                           ('occupancyMed', 4), ('occupancyHigh', 5),
                           ('occupancyNearlyFull', 6), ('occupancyFull', 7)]
            },
            'TransitVehicleStatus': {
                'type':
                'BIT STRING',
                'named-bits': [('loading', '0'), ('anADAuse', '1'),
                               ('aBikeLoad', '2'), ('doorOpen', '3'),
                               ('charging', '4'), ('atStopLine', '5')],
                'size': [8]
            },
            'TransmissionState': {
                'type':
                'ENUMERATED',
                'values': [('neutral', 0), ('park', 1), ('forwardGears', 2),
                           ('reverseGears', 3), ('reserved1', 4),
                           ('reserved2', 5), ('reserved3', 6),
                           ('unavailable', 7)]
            },
            'VehicleHeight': {
                'type': 'INTEGER',
                'restricted-to': [(0, 127)]
            },
            'VehicleType': {
                'type':
                'ENUMERATED',
                'values': [('none', 0), ('unknown', 1), ('special', 2),
                           ('moto', 3), ('car', 4), ('carOther', 5),
                           ('bus', 6), ('axleCnt2', 7), ('axleCnt3', 8),
                           ('axleCnt4', 9), ('axleCnt4Trailer', 10),
                           ('axleCnt5Trailer', 11), ('axleCnt6Trailer', 12),
                           ('axleCnt5MultiTrailer', 13),
                           ('axleCnt6MultiTrailer', 14),
                           ('axleCnt7MultiTrailer', 15), None]
            },
            'Velocity': {
                'type': 'INTEGER',
                'restricted-to': [(0, 8191)]
            },
            'WaitOnStopline': {
                'type': 'BOOLEAN'
            },
            'ZoneLength': {
                'type': 'INTEGER',
                'restricted-to': [(0, 10000)]
            }
        },
        'values': {
            'mapData': {
                'type': 'DSRCmsgID',
                'value': 18
            },
            'rtcmCorrections': {
                'type': 'DSRCmsgID',
                'value': 28
            },
            'signalPhaseAndTimingMessage': {
                'type': 'DSRCmsgID',
                'value': 19
            },
            'signalRequestMessage': {
                'type': 'DSRCmsgID',
                'value': 29
            },
            'signalStatusMessage': {
                'type': 'DSRCmsgID',
                'value': 30
            },
            'unknownFuel': {
                'type': 'FuelType',
                'value': 0
            },
            'gasoline': {
                'type': 'FuelType',
                'value': 1
            },
            'ethanol': {
                'type': 'FuelType',
                'value': 2
            },
            'diesel': {
                'type': 'FuelType',
                'value': 3
            },
            'electric': {
                'type': 'FuelType',
                'value': 4
            },
            'hybrid': {
                'type': 'FuelType',
                'value': 5
            },
            'hydrogen': {
                'type': 'FuelType',
                'value': 6
            },
            'natGasLiquid': {
                'type': 'FuelType',
                'value': 7
            },
            'natGasComp': {
                'type': 'FuelType',
                'value': 8
            },
            'propane': {
                'type': 'FuelType',
                'value': 9
            },
            'noRegion': {
                'type': 'RegionId',
                'value': 0
            },
            'addGrpA': {
                'type': 'RegionId',
                'value': 1
            },
            'addGrpB': {
                'type': 'RegionId',
                'value': 2
            },
            'addGrpC': {
                'type': 'RegionId',
                'value': 3
            }
        },
        'object-classes': {
            'REG-EXT-ID-AND-TYPE': {
                'members': [{
                    'type': 'RegionId',
                    'name': '&id'
                }, {
                    'type': 'OpenType',
                    'name': '&Type'
                }]
            }
        },
        'object-sets': {},
        'extensibility-implied': False,
        'tags': 'AUTOMATIC'
    }
}
