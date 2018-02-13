import rdflib
from sbol import *

SD2_NS = 'http://sd2e.org#'

OM_NS = 'http://www.ontology-of-units-of-measure.org/resource/om-2#'

PROV_NS = 'http://www.w3.org/ns/prov#'

class Experiment(TopLevel):
    
    def __init__(self, displayId, experimentalData=None, version='1.0.0'):
        TopLevel.__init__(self, SD2_NS + 'Experiment', displayId, version)
        self.identity = self.identity.replace('/Experiment', '')
        self.persistentIdentity = self.persistentIdentity.replace('/Experiment', '')
        self.experimentalData = experimentalData if experimentalData is not None else URIProperty(SD2_NS + 'experimentalData', self.this)
        self.register_extension_class(Experiment, 'sd2')

class ExperimentalData(TopLevel):
    
    def __init__(self, displayId, attachments=None, version='1.0.0'):
        TopLevel.__init__(self, SD2_NS + 'ExperimentalData', displayId, version)
        self.identity = self.identity.replace('/ExperimentalData', '')
        self.persistentIdentity = self.persistentIdentity.replace('/ExperimentalData', '')
        self.attachments = attachments if attachments is not None else URIProperty(SD2_NS + 'attachment', self.this)
        self.register_extension_class(ExperimentalData, 'sd2')

class Attachment(TopLevel):
    
    def __init__(self, displayId, source=None, format=None, size=None, hash=None, version = '1.0.0'):
        TopLevel.__init__(self, SD2_NS + 'Attachment', displayId, version)
        self.identity = self.identity.replace('/Attachment', '')
        self.persistentIdentity = self.persistentIdentity.replace('/Attachment', '')
        self.source = source if source is not None else URIProperty(SD2_NS + 'source', self.this)
        self.format = format if format is not None else URIProperty(SD2_NS + 'format', self.this)
        self.size = size
        self.hash = hash
        self.register_extension_class(Attachment, 'sd2')
        
class Implementation(TopLevel):
    
    def __init__(self, displayId, built=None, version='1.0.0'):
        TopLevel.__init__(self, SD2_NS + 'Implementation', displayId, version)
        self.identity.set(self.identity.replace('/Implementation', ''))
        self.persistentIdentity.set(self.persistentIdentity.replace('/Implementation', ''))
        self.built = built if built is not None else URIProperty(SD2_NS + 'built', self.this)
        self.register_extension_class(Implementation, 'sd2')

class Measure(Identified):
    
    def __init__(self, displayId, hasNumericalValue=None, hasUnit=None):
        Identified.__init__(self, OM_NS + 'Measure', displayId)
        self.identity = self.identity.replace('/Measure', '')
        self.persistentIdentity = self.persistentIdentity.replace('/Measure', '')
        self.hasNumericalValue = hasNumericalValue if hasNumericalValue is not None else FloatProperty(OM_NS + "hasNumericalValue", self.this)
        self.hasUnit = hasUnit if hasUnit is not None else URIProperty(OM_NS + 'hasUnit', self.this)
        self.register_extension_class(Measure, 'om')
        
class Unit(TopLevel):
    
    def __init__(self, displayId, symbol=None):
        TopLevel.__init__(self, OM_NS + 'Unit', displayId)
        self.identity = self.identity.replace('/Unit', '')
        self.persistentIdentity = self.persistentIdentity.replace('/Unit', '')
        self.symbol = symbol if symbol is not None else TextProperty(OM_NS + "symbol", self.this)
        self.register_extension_class(Unit, 'om')

class Channel(Identified):
    
    def __init__(self, displayId, calibrationFile=None):
        Identified.__init__(self, SD2_NS + 'Channel', displayId)
        self.identity = self.identity.replace('/Channel', '')
        self.persistentIdentity = self.persistentIdentity.replace('/Channel', '')
        self.calibrationFile = calibrationFile if calibrationFile is not None else URIProperty(SD2_NS + 'calibrationFile', self.this)
        self.register_extension_class(Channel, 'sd2')

class XDocument(Document):

    def __init__(self):
        super(XDocument, self).__init__()

    def generate_uri(self, prefix, display_id, version=None):
        uri_arr = [prefix]
        uri_arr.append('/')
        uri_arr.append(display_id)
        if version is not None:
            uri_arr.append('/')
            uri_arr.append(version)
    
        return ''.join(uri_arr)

    def add_top_levels(self, top_levels, collect=None):
        for top_level in top_levels:
            try:
                top_level.addToDocument(self)

                if collect is not None:
                    self.add_member(top_level, collect)
            except:
                pass

    def add_custom(self, sbol_obj, custom):
        for i in range(0, len(custom) - 1, 2):
            if repr(custom[i]).replace('.', '').isnumeric():
                setattr(sbol_obj, custom[i + 1], FloatProperty(SD2_NS + custom[i + 1], sbol_obj))
                getattr(sbol_obj, custom[i + 1]).set(custom[i])
            else:
                setattr(sbol_obj, custom[i + 1], URIProperty(SD2_NS + custom[i + 1], sbol_obj))
                getattr(sbol_obj, custom[i + 1]).add(custom[i])

    def add_measures(self, sbol_obj, measures):
        if len(measures) > 0:
            if not hasattr(sbol_obj, 'measures'):
                sbol_obj.measures = OwnedPythonObject(Measure, SD2_NS + 'measure', sbol_obj)
            for measure in measures:
                try:
                    self.create_measure(measure['mag'], sbol_obj, measure['unit'], measure['id'])
                except:
                    try:
                        self.create_measure(measure['mag'], sbol_obj, measure['unit'])
                    except:
                        self.create_measure(mag=measure['mag'], sbol_obj=sbol_obj, display_id=measure['id'])

    def add_member(self, sbol_obj, collect):
        collect.members.append(bol_obj.identity)

    def configure_options(self, homespace, is_validated, is_typed):
        setHomespace(homespace)
        Config.setOption('validate', is_validated)
        Config.setOption('sbol_typed_uris', is_typed)

    def create_collection(self, display_id, name):
        try:
            collect = self.collections.create(display_id)
            collect.name = name
        except:
            collect = self.getCollection(self.generate_uri(getHomespace(), display_id, '1.0.0'))
        
        return collect

    def create_component_definition(self, display_id, name, comp_type=None, comp_role=None):
        try:
            comp_def = self.componentDefinitions.create(display_id)
            comp_def.name = name
            if comp_type is not None:
                comp_def.types = [comp_type]
            else:
                comp_def.types = []
            if comp_role is not None:
                comp_def.roles = [comp_role]
            else:
                comp_def.roles = []
        except:
            comp_def = self.getComponentDefinition(self.generate_uri(getHomespace(), display_id, '1.0.0'))

        return comp_def

    def create_inducer(self, display_id, name):
        return self.create_component_definition(display_id, name, BIOPAX_SMALL_MOLECULE, 'http://identifiers.org/chebi/CHEBI:35224')

    def create_plasmid(self, display_id, name):
        plasmid = self.create_component_definition(display_id, name, BIOPAX_DNA)
        plasmid.types.append('http://identifiers.org/so/SO:0000988')

        return plasmid

    def create_strain(self, display_id, name):
        return self.create_component_definition(display_id, name, 'http://purl.obolibrary.org/obo/OBI_0100060')

    def create_module_definition(self, display_id, name, mod_role=None):
        try:
            mod_def = self.moduleDefinitions.create(display_id)
            mod_def.name = name
            if mod_role is not None:
                mod_def.roles = [mod_role]
            else:
                mod_def.roles = []
        except:
            mod_def = self.getModuleDefinition(self.generate_uri(getHomespace(), display_id, '1.0.0'))

        return mod_def

    def create_module(self, mod_def, parent_mod_def):
        try:
            mod = parent_mod_def.modules.create(mod_def.displayId)
            mod.definition = mod_def.identity
        except:
            mod = parent_mod_def.modules.get(mod_def.displayId)

        return mod

    def create_functional_component(self, comp_def, mod_def):
        try:
            fc = mod_def.functionalComponents.create(comp_def.displayId)
            fc.definition = comp_def.identity
        except:
            fc = mod_def.functionalComponents.get(comp_def.displayId)

        return fc

    def create_input_component(self, comp_def, mod_def):
        fc = self.create_functional_component(comp_def, mod_def)
        fc.direction = SBOL_DIRECTION_IN

        return fc

    def create_measure(self, mag, sbol_obj, unit=None, display_id=None, name=None):
        if display_id is not None:
            ms_id = display_id
        else:
            ms_id = sbol_obj.displayId + '_measure'

        try:
            ms = sbol_obj.measures.create(ms_id)
            if name is not None:
                ms.name = name
            else:
                ms.name = ms_id
            ms.hasNumericalValue = mag
            if unit is not None:
                ms.hasUnit.append(unit.identity)
        except:
            pass
            # ms = fc.measure.get(self.generate_uri(fc.persistentIdentity.get(), ms_id, '1.0.0'))
        
    def create_unit(self, om, symbol=None, display_id=None, name=None, descr=None):
        try:
            uri = ''.join(['<', OM_NS[:-1], '/', display_id, '>'])
            result = next(iter(om.query(''.join(["SELECT ?symbol ?name ?descr WHERE { ", uri, " om:symbol ?symbol ; rdfs:label ?name . OPTIONAL { ", uri, " rdfs:comment ?descr . FILTER (lang(?descr) = 'en') . } FILTER (lang(?name) = 'en') }"]))))
        except:
            try:
                result = next(iter(om.query(''.join(["SELECT ?uri ?name ?descr WHERE { ?uri om:symbol '", symbol, "' ; rdfs:label ?name . OPTIONAL { ?uri rdfs:comment ?descr . FILTER (lang(?descr) = 'en') . } FILTER (lang(?name) = 'en') }"]))))
            except:
                result = next(iter(om.query(''.join(["SELECT ?uri ?symbol ?descr WHERE { ?uri om:symbol ?symbol . {?uri rdfs:label '", name, "'@en . } UNION {?uri rdfs:label '", name, "'@nl } }"]))))

        try:
            unit_id = result.uri.split('/')[-1]
        except:
            unit_id = display_id

        unit = Unit(unit_id)

        try:
            unit.name = result.name
        except:
            if name is not None:
                unit.name = name
            else:
                unit.name = unit_id
        try:
            unit.description = result.descr
        except:
            if descr is not None:
                unit.description = descr

        try:
            unit.symbol = result.symbol
        except:
            if symbol is not None:
                unit.symbol = symbol

        try:
            unit.wasDerivedFrom.append(result.uri)
        except:
            unit.wasDerivedFrom.append(''.join([OM_NS[:-1], '/', display_id]))

        return unit

    def create_system(self, devices=[], sub_systems=[], inputs=[], measures=[], display_id=None, name=None):
        id_arr = []
        if display_id is not None:
            id_arr.append(display_id)
        else:
            if len(devices) > 0:
                for device in devices:
                    id_arr.append(device.displayId)
                    id_arr.append('_')
            elif len(sub_systems) > 0:
                for sub_system in sub_systems:
                    id_arr.append(sub_system.displayId.replace('_system', ''))
                    id_arr.append('_')
            for i in range(0, len(inputs)):
                id_arr.append(inputs[i].displayId)
                id_arr.append('_')
                if i < len(measures):
                    id_arr.append(measures[i]['mag'].replace('.', 'p'))
                    id_arr.append('_')
            id_arr.append('system')
        system_id = ''.join(id_arr)

        system = self.create_module_definition(system_id, system_id)

        for device in devices:
            self.create_functional_component(device, system)

        for sub_system in sub_systems:
            self.create_module(sub_system, system)

        for i in range(0, len(inputs)):
            fc = self.create_input_component(inputs[i], system)

            if i < len(measures):
                self.add_measures(fc, [measures[i]])
                # if not hasattr(fc, 'measures'):
                #     fc.measures = OwnedPythonObject(Measure, SD2_NS + 'measure', fc)
                # try:
                #     self.create_measure(measures[i]['mag'], fc, measures[i]['unit'])
                # except:
                #     self.create_measure(measures[i]['mag'], fc)

        return system

    def create_flow_cytometry_activity(self, operator, channels=[], parents=[], name=None, description=None, custom=[], child=None, display_id=None):
        act = create_activity(operator, parents, name, description, custom, child, display_id)

        if len(channels) > 0 and not hasattr(act, 'channels'):
            act.channels = OwnedPythonObject(Channel, SD2_NS + 'channel', act)

        for channel in channels:
            self.create_channel(channel.display_id, channel.calibration_file, act, channel.name)

    def create_activity(self, operator, parents=[], name=None, description=None, custom=[], child=None, display_id=None):
        id_arr = []
        if display_id is not None:
            id_arr.append(display_id)
        else:
            id_arr.append(operator)
            parent_id_arr = []
            for parent in parents:
                if isinstance(parent, Activity):
                    for entity in self.get_parent_entities(parent):
                        parent_id_arr.append('_')
                        parent_id_arr.append(entity.displayId)
                else:
                    parent_id_arr.append('_')
                    parent_id_arr.append(parent.displayId)
            if len(parent_id_arr) > 0:
                id_arr.extend(parent_id_arr)
                if child is not None:
                    id_arr.append('_to')
            if child is not None:
                id_arr.append('_')
                id_arr.append(child.displayId)
        act_id = ''.join(id_arr)

        try:
            act = self.activities.create(act_id)
            if name is not None:
                act.name = name
            else:
                act.name = act_id
            if description is not None:
                act.description = description

            for parent in parents:
                if isinstance(parent, Activity):
                    try:
                        act.wasInformedBy.add(parent.identity)
                    except:
                        act.wasInformedBy = URIProperty(PROV_NS + 'wasInformedBy', act)
                        act.wasInformedBy.add(parent.identity)
                else:
                    try:
                        act.used.add(parent.identity)
                    except:
                        act.used = URIProperty(PROV_NS + 'used', act)
                        act.used.add(parent.identity)

            act.operator = URIProperty(SD2_NS + 'operatorType', act)
            act.operator.add(SD2_NS + operator)

            self.add_custom(act, custom)
            
            if child is not None:
                child.wasGeneratedBy.append(act.identity)
        except:
            act = self.activities.get(act_id)
            
        return act

    def create_channel(self, channel_id, calibration_file, act, name=None, display_id=None):
        try:
            if display_id is not None:
                channel = act.channels.create(display_id, calibration_file)
            else:
                channel = act.channels.create(channel_id, calibration_file)
            if name is not None:
                channel.name = name
            else:
                channel.name = channel.displayId
        except:
            pass
            # act.channels.get(generate_uri(act.persistentIdentity.get(), channel_id, '1.0.0'))

    def create_attachment(self, display_id, name, source, attach_format=None):
        attach = Attachment(display_id)
        attach.name = name
        attach.source = source
        if attach_format is not None:
            attach.format.add(attach_format)
        
        return attach

    def create_experimental_data(self, attachs, imp, exp, operator=None, replicate_id=None, display_id=None, name=None):
        id_arr = []
        if display_id is not None:
            id_arr.append(display_id)
        else:
            id_arr.append(imp.displayId)
            if operator is not None:
                id_arr.append('_')
                id_arr.append(operator)
            if replicate_id is not None:
                id_arr.append('_')
                id_arr.append(replicate_id)
                
        exp_datum_id = ''.join(id_arr)

        exp_datum = ExperimentalData(exp_datum_id)
        if name is not None:
            exp_datum.name = name
        else:
            exp_datum.name = exp_datum_id
        for attach in attachs:
            exp_datum.attachments.add(attach.identity)

        exp_datum.wasDerivedFrom.append(imp.identity)
        
        exp.experimentalData.add(exp_datum.identity)
        
        return exp_datum

    def create_implementation(self, display_id, name, built=None, parents=[]):
        imp = Implementation(display_id)

        imp.name = name
        if built is not None:
            imp.built.add(built.identity)
        
        for parent in parents:
            imp.wasDerivedFrom.append(parent.identity)

        return imp

    def create_sample(self, sample_id, built=None, parent_samples=[], well_id=None, plate_id=None):
        id_arr = []
        if plate_id is not None:
            id_arr.append(plate_id)
            id_arr.append('_')
        if well_id is not None:
            id_arr.append(well_id)
            id_arr.append('_')
        id_arr.append(sample_id)
        sample_id = ''.join(id_arr)
        
        sample = self.create_implementation(sample_id, sample_id, built, parent_samples)

        return sample

    def create_experiment(self, display_id, name):
        exp = Experiment(display_id)
        exp.name = name

        return exp

    def get_devices(self, uris):
        devices = []

        for uri in uris:
            try:
                devices.append(self.getComponentDefinition(uri))
            except:
                pass

        return devices

    def get_systems(self, uris):
        systems = []

        for uri in uris:
            try:
                systems.append(self.getModuleDefinition(uri))
            except:
                pass

        return systems

    def get_collection_members(self, collect):
        top_levels = []

        for member in collect.members:
            try:
                top_levels.append(self.getTopLevel(member))
            except:
                pass

        return top_levels

    def get_parent_entities(self, act):
        parent_entities = []

        acts = [act]

        while True:
            try:
                curr_act = acts.pop()
            except:
                break

            try:
                for uri in curr_act.getPropertyValues(PROV_NS + 'used'):
                    parent_entities.append(self.getTopLevel(uri))
            except:
                pass

            for uri in curr_act.wasInformedBy.getAll():
                if len(uri) > 0:
                    acts.append(self.activities.get(uri))

        return parent_entities

    def read(self, sbol_path):
        super(XDocument, self).read(sbol_path)

    def read_om(self, om_path):
        om = rdflib.Graph()
        om.parse(om_path)

        return om

    def write(self, sbol_path):
        super(XDocument, self).write(sbol_path)

    def upload(self, sbh_address, sbh_email, sbh_password):
        part_shop = PartShop(sbh_address)
        part_shop.login(sbh_email, sbh_password)
        part_shop.submit(self)