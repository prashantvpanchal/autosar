import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
import autosar
from tests.arxml.common import ARXMLTestClass
import unittest

def _create_packages(ws):

    package=ws.createPackage('DataTypes', role='DataType')
    package.createSubPackage('CompuMethods', role='CompuMethod')
    package.createSubPackage('DataConstrs', role='DataConstraint')
    package.createSubPackage('Units', role='Unit')
    package.createSubPackage('BaseTypes')
    package = ws.createPackage('ModeDclrGroups', role = 'ModeDclrGroup')
    package = ws.createPackage('Constants', role='Constant')
    package = ws.createPackage('ComponentTypes', role='ComponentType')
    package = ws.createPackage('PortInterfaces', role='PortInterface')


def _create_data_types(ws):
    basetypes = ws.find('/DataTypes/BaseTypes')
    basetypes.createSwBaseType('boolean', 1, 'BOOLEAN')
    basetypes.createSwBaseType('uint8', 8, nativeDeclaration='uint8')
    basetypes.createSwBaseType('uint16', 16, nativeDeclaration='uint16')
    basetypes.createSwBaseType('uint32', 32, nativeDeclaration='uint32')
    basetypes.createSwBaseType('float32', 32, encoding='IEEE754')
    package = ws.find('DataTypes')
    package.createImplementationDataType('boolean', valueTable=['FALSE','TRUE'], baseTypeRef='/DataTypes/BaseTypes/boolean', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint8', lowerLimit=0, upperLimit=255, baseTypeRef='/DataTypes/BaseTypes/uint8', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint16', lowerLimit=0, upperLimit=65535, baseTypeRef='/DataTypes/BaseTypes/uint16', typeEmitter='Platform_Type')
    package.createImplementationDataType('uint32', lowerLimit=0, upperLimit=4294967295, baseTypeRef='/DataTypes/BaseTypes/uint32', typeEmitter='Platform_Type')
    package.createImplementationDataTypeRef('OffOn_T', implementationTypeRef = '/DataTypes/uint8',
                                            valueTable = ['OffOn_Off',
                                                          'OffOn_On',
                                                          'OffOn_Error',
                                                          'OffOn_NotAvailable'
                                                        ])
    package.createImplementationDataTypeRef('Seconds_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=63)
    package.createImplementationDataTypeRef('Minutes_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=63)
    package.createImplementationDataTypeRef('Hours_T', '/DataTypes/uint8', lowerLimit=0, upperLimit=31)
    package.createImplementationDataTypeRef('VehicleSpeed_T', '/DataTypes/uint16')
    package.createImplementationDataTypeRef('EngineSpeed_T', '/DataTypes/uint16')

def _create_port_interfaces(ws):
    package = ws.find('/PortInterfaces')
    package.createSenderReceiverInterface('VehicleSpeed_I', autosar.DataElement('VehicleSpeed', 'VehicleSpeed_T'))
    package.createSenderReceiverInterface('EngineSpeed_I', autosar.DataElement('EngineSpeed', 'EngineSpeed_T'))
    portInterface=package.createClientServerInterface('FreeRunningTimer5ms_I', ['GetTime', 'IsTimerElapsed'])
    portInterface['GetTime'].createOutArgument('value', 'uint32')
    portInterface['IsTimerElapsed'].createInArgument('startTime', 'uint32')
    portInterface['IsTimerElapsed'].createInArgument('duration', 'uint32')
    portInterface['IsTimerElapsed'].createOutArgument('result', 'boolean')
    package.createModeSwitchInterface('VehicleMode_I', autosar.mode.ModeGroup('mode', 'VehicleMode'))

def _create_constants(ws):
    package = ws.find('/Constants')
    package.createConstant('VehicleSpeed_IV', 'VehicleSpeed_T', 65535)
    package.createConstant('EngineSpeed_IV', 'EngineSpeed_T', 65535)


def _create_mode_declarations(ws):
    package = ws.find('ModeDclrGroups')
    package.createModeDeclarationGroup('VehicleMode', ["OFF",
                                                       "ACCESSORY",
                                                        "RUNNING",
                                                        "CRANKING",
                                                    ], "OFF")

def _init_ws():
    ws = autosar.workspace('4.2.2')
    _create_packages(ws)
    _create_data_types(ws)
    _create_mode_declarations(ws)
    _create_port_interfaces(ws)
    _create_constants(ws)

    return ws

class ARXML4BehaviorTest(ARXMLTestClass):

    def test_create_empty_behavior_from_swc(self):

        ws = _init_ws()
        swc1 = ws['ComponentTypes'].createApplicationSoftwareComponent('MyApplication')
        file_name = 'ar4_behavior_empty_from_swc.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'behavior', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_runnable_with_init_event(self):

        ws = _init_ws()
        swc1 = ws['ComponentTypes'].createApplicationSoftwareComponent('MyApplication')
        swc1.behavior.createRunnable('MyApplication_Init')
        swc1.behavior.createInitEvent('MyApplication_Init')

        file_name = 'ar4_runnable_with_init_event.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'behavior', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_runnable_with_require_type_mode_switch_trigger(self):

        ws = _init_ws()
        swc1 = ws['ComponentTypes'].createApplicationSoftwareComponent('MyApplication')
        swc1.createRequirePort('VehicleMode', '/PortInterfaces/VehicleMode_I')
        swc1.behavior.createRunnable('MyApplication_Init')
        swc1.behavior.createModeSwitchEvent('MyApplication_Init', 'VehicleMode/ACCESSORY', activationType='ENTRY')

        file_name = 'ar4_runnable_with_require_type_mode_switch_trigger.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'behavior', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)

    def test_create_runnable_with_provide_type_mode_access(self):

        ws = _init_ws()
        swc1 = ws['ComponentTypes'].createApplicationSoftwareComponent('MyApplication')
        port1 = swc1.createProvidePort('VehicleMode', '/PortInterfaces/VehicleMode_I', queueLength=1, modeSwitchAckTimeout=10)
        runnable1 = swc1.behavior.createRunnable('MyApplication_Init', portAccess=['VehicleMode'])

        file_name = 'ar4_runnable_with_provide_type_mode_access.arxml'
        generated_file = os.path.join(self.output_dir, file_name)
        expected_file = os.path.join( 'expected_gen', 'behavior', file_name)
        self.save_and_check(ws, expected_file, generated_file, ['/ComponentTypes'])

        ws2 = autosar.workspace(ws.version_str)
        ws2.loadXML(os.path.join(os.path.dirname(__file__), expected_file))
        swc2 = ws2.find(swc1.ref)
        self.assertIsInstance(swc2, autosar.component.ApplicationSoftwareComponent)
        port2 = ws2.find(port1.ref)
        self.assertIsInstance(port2, autosar.component.ProvidePort)
        runnable2 = swc2.behavior.find(runnable1.name)
        self.assertIsInstance(runnable2, autosar.behavior.RunnableEntity)
        modeAccessPoint = runnable2.modeAccessPoints[0]
        self.assertEqual(modeAccessPoint.modeGroupRef, '/PortInterfaces/VehicleMode_I/mode')
        self.assertEqual(modeAccessPoint.providePortRef, '/ComponentTypes/MyApplication/VehicleMode')


if __name__ == '__main__':

    unittest.main()
