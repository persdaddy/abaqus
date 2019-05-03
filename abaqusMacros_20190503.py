# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__


def TestModel():
    '''
    def __init__():

    '''

    #### CONSTANTS ####
    model_name = "New"
    part_name = 'Plate'
    material_name = 'Steel'
    modulus_of_elasticity = 30000000.0
    poissons = 0.3
    section_name = 'plate_section'
    edge_list = ['left_edge', 'bottom_edge', 'right_edge', 'top_edge']
    surface_name = 'plate_face'

    #### VARIABLES ####
    pressure = 1000.0
    x_len_ft = 2.0
    y_len_ft = 8.0

    x_min_inch = x_len_ft * -12.0 / 2.0
    x_max_inch = x_len_ft * 12.0 / 2.0
    y_min_inch = y_len_ft * -12.0 / 2.0
    y_max_inch = y_len_ft * 12.0 / 2.0

    sketch_points = [(x_min_inch, y_min_inch), (x_max_inch, y_max_inch)]
    print sketch_points[0], sketch_points[1]

    #new_model()
    sketch_make_part(part_name, sketch_points)
    make_material(material_name, modulus_of_elasticity, poissons)
    make_shell_section(section_name, material_name)
    assign_section(section_name, part_name)
    instance(part_name)
    make_edge_sets(part_name, edge_list)
    seed_and_mesh(part_name)
    make_BCs(edge_list)
    make_loading_surface(part_name, surface_name)
    make_step()
    load_surface(surface_name, pressure)
    make_job(pressure)


def new_model():
    mdb.Model(name='Model-1', modelType=STANDARD_EXPLICIT)


def sketch_make_part(part_name, sketch_points):
    print "Sketching part..."
    s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                 sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.rectangle(point1=sketch_points[0], point2=sketch_points[1])

    p = mdb.models['Model-1'].Part(name=part_name, dimensionality=THREE_D,
                                   type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts[part_name]
    p.BaseShell(sketch=s1)
    p = mdb.models['Model-1'].parts[part_name]
    del mdb.models['Model-1'].sketches['__profile__']


def make_material(material_name, modulus_of_elasticity, poissons):
    print "Making material..."
    mdb.models['Model-1'].Material(name=material_name)
    mdb.models['Model-1'].materials[material_name].Elastic(table=((modulus_of_elasticity, poissons),))


# NEEDS CHANGES
def change_material_props():
    mdb.models['Model-1'].materials['steel'].elastic.setValues(table=((30000000.0,
                                                                       0.3),))


def make_shell_section(section_name, material_name):
    print "Making Shell Section..."
    mdb.models['Model-1'].HomogeneousShellSection(name=section_name,
                                                  preIntegrate=OFF, material=material_name, thicknessType=UNIFORM,
                                                  thickness=0.375, thicknessField='', nodalThicknessField='',
                                                  idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT,
                                                  thicknessModulus=None, temperature=GRADIENT, useDensity=OFF,
                                                  integrationRule=SIMPSON, numIntPts=5)


def assign_section(section_name, part_name):
    print "Assigning section to part..."
    p = mdb.models['Model-1'].parts[part_name]
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#1 ]',), )
    region = p.Set(faces=faces, name='Set-1')
    p = mdb.models['Model-1'].parts[part_name]
    p.SectionAssignment(region=region, sectionName=section_name, offset=0.0,
                        offsetType=MIDDLE_SURFACE, offsetField='',
                        thicknessAssignment=FROM_SECTION)


def instance(part_name):
    print "Creating an instance of the part..."
    a = mdb.models['Model-1'].rootAssembly
    p = mdb.models['Model-1'].parts[part_name]
    a.Instance(name=part_name + '-1', part=p, dependent=ON)


def make_edge_sets(part_name, edge_list):
    print "Making sets from the edges..."
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances[part_name + '-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#8 ]',), )
    a.Set(edges=edges1, name=edge_list[0])

    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances[part_name + '-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
    a.Set(edges=edges1, name=edge_list[1])

    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances[part_name + '-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#2 ]',), )
    a.Set(edges=edges1, name=edge_list[2])

    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances[part_name + '-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#4 ]',), )
    a.Set(edges=edges1, name=edge_list[3])


def seed_and_mesh(part_name):
    print "Seeding and meshing the part..."
    p = mdb.models['Model-1'].parts[part_name]
    e = p.edges
    pickedEndEdges = e.getSequenceFromMask(mask=('[#f ]',), )
    try:
        p.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges, minSize=3.0,
                         maxSize=6.0, constraint=FINER)
    except:
        p.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges, minSize=4.0,
                         maxSize=6.0, constraint=FINER)
    p.generateMesh()


def change_BCs():
    bcs = ['right_', 'left_', 'bottom_', 'top_']
    prev = 'fixed'
    cond = 'fixed'
    dofs = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for bc in bcs:
        prev_bc_name = bc + prev
        new_bc_name = bc + cond
        print prev_bc_name, new_bc_name
        mdb.models['Model-1'].boundaryConditions.changeKey(fromName=prev_bc_name,
                                                           toName=new_bc_name)
        mdb.models['Model-1'].boundaryConditions[new_bc_name].setValues(u1=UNSET,
                                                                        u2=UNSET, u3=UNSET, ur1=dofs[3], ur2=dofs[4],
                                                                        ur3=dofs[5])


def make_BCs(edge_list):
    print "Making boundary conditions..."
    for edge in edge_list:
        a = mdb.models['Model-1'].rootAssembly
        region = a.sets[edge]
        mdb.models['Model-1'].DisplacementBC(name=edge + 'BC', createStepName='Initial',
                                             region=region, u1=SET, u2=SET, u3=SET, ur1=SET, ur2=SET, ur3=SET,
                                             amplitude=UNSET, distributionType=UNIFORM, fieldName='',
                                             localCsys=None)


def make_loading_surface(part_name, surface_name):
    print "Creating surface for loading..."
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances[part_name + '-1'].faces
    side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]',), )
    a.Surface(side2Faces=side2Faces1, name=surface_name)


def make_step():
    print "Making new loading step..."
    mdb.models['Model-1'].StaticStep(name='Loading', previous='Initial',
                                     description='surface_pressure')


def load_surface(surface_name, pressure):
    print "Applying load to surface..."
    a = mdb.models['Model-1'].rootAssembly
    region = a.surfaces[surface_name]
    mdb.models['Model-1'].Pressure(name='plate_pressure', createStepName='Loading',
                                   region=region, distributionType=UNIFORM, field='', magnitude=pressure,
                                   amplitude=UNSET)


def make_job(pressure):
    print "Making job..."
    mdb.Job(name='Pressure_' + str(int(pressure)), model='Model-1', description='', type=ANALYSIS,
            atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90,
            memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch='', resultsFormat=ODB)


def ThreeD_plate():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    s1 = mdb.models['Model-1'].ConstrainedSketch(name='__profile__',
                                                 sheetSize=200.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.setPrimaryObject(option=STANDALONE)
    s1.rectangle(point1=(-24.0, -48.0), point2=(24.0, 48.0))
    p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D,
                                   type=DEFORMABLE_BODY)
    p = mdb.models['Model-1'].parts['Part-1']
    p.BaseShell(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p)
    del mdb.models['Model-1'].sketches['__profile__']

    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=ON,
                                                           engineeringFeatures=ON)
    session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
        referenceRepresentation=OFF)

    mdb.models['Model-1'].Material(name='steel')
    mdb.models['Model-1'].materials['steel'].Elastic(table=((30000.0, 0.28),))

    mdb.models['Model-1'].HomogeneousShellSection(name='Section-1',
                                                  preIntegrate=OFF, material='steel', thicknessType=UNIFORM,
                                                  thickness=0.375, thicknessField='', nodalThicknessField='',
                                                  idealization=NO_IDEALIZATION, poissonDefinition=DEFAULT,
                                                  thicknessModulus=None, temperature=GRADIENT, useDensity=OFF,
                                                  integrationRule=SIMPSON, numIntPts=5)

    a = mdb.models['Model-1'].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    a1 = mdb.models['Model-1'].rootAssembly
    a1.DatumCsysByDefault(CARTESIAN)
    p = mdb.models['Model-1'].parts['Part-1']
    a1.Instance(name='Part-1-1', part=p, dependent=ON)
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#8 ]',), )
    a.Set(edges=edges1, name='Left edge')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#8 ]',), )
    a.Set(edges=edges1, name='Left edge')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#8 ]',), )
    a.Set(edges=edges1, name='Left edge')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#2 ]',), )
    a.Set(edges=edges1, name='right_edge')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#4 ]',), )
    a.Set(edges=edges1, name='top_edge')
    a = mdb.models['Model-1'].rootAssembly
    e1 = a.instances['Part-1-1'].edges
    edges1 = e1.getSequenceFromMask(mask=('[#1 ]',), )
    a.Set(edges=edges1, name='bottom_edge')
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#1 ]',), )
    a.Surface(side1Edges=side1Edges1, name='bottom_surf')
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#4 ]',), )
    a.Surface(side1Edges=side1Edges1, name='top_surf')
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#8 ]',), )
    a.Surface(side1Edges=side1Edges1, name='left_surf')
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].edges
    side1Edges1 = s1.getSequenceFromMask(mask=('[#2 ]',), )
    a.Surface(side1Edges=side1Edges1, name='right_surf')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                               predefinedFields=ON, connectors=ON)
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets['Left edge']
    mdb.models['Model-1'].DisplacementBC(name='left_pins',
                                         createStepName='Initial', region=region, u1=SET, u2=SET, u3=UNSET,
                                         ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET,
                                         distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-1'].rootAssembly
    region = a.sets['right_edge']
    mdb.models['Model-1'].DisplacementBC(name='right_pins',
                                         createStepName='Initial', region=region, u1=SET, u2=SET, u3=UNSET,
                                         ur1=UNSET, ur2=UNSET, ur3=UNSET, amplitude=UNSET,
                                         distributionType=UNIFORM, fieldName='', localCsys=None)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                               predefinedFields=OFF, connectors=OFF,
                                                               adaptiveMeshConstraints=ON)
    mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=ON, bcs=ON,
                                                               predefinedFields=ON, connectors=ON,
                                                               adaptiveMeshConstraints=OFF)
    a = mdb.models['Model-1'].rootAssembly
    region = a.surfaces['bottom_surf']
    mdb.models['Model-1'].Pressure(name='bottom_pressure', createStepName='Step-1',
                                   region=region, distributionType=UNIFORM, field='', magnitude=1000.0,
                                   amplitude=UNSET)
    a = mdb.models['Model-1'].rootAssembly
    region = a.surfaces['top_surf']
    mdb.models['Model-1'].Pressure(name='top_pressure', createStepName='Step-1',
                                   region=region, distributionType=UNIFORM, field='', magnitude=1000.0,
                                   amplitude=UNSET)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(loads=OFF, bcs=OFF,
                                                               predefinedFields=OFF, connectors=OFF)
    session.viewports['Viewport: 1'].partDisplay.setValues(sectionAssignments=OFF,
                                                           engineeringFeatures=OFF, mesh=ON)
    session.viewports['Viewport: 1'].partDisplay.meshOptions.setValues(
        meshTechnique=ON)
    p1 = mdb.models['Model-1'].parts['Part-1']
    session.viewports['Viewport: 1'].setValues(displayedObject=p1)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    pickedEndEdges = e.getSequenceFromMask(mask=('[#5 ]',), )
    p.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges, minSize=0.96,
                     maxSize=4.8, constraint=FINER)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    pickedEndEdges = e.getSequenceFromMask(mask=('[#5 ]',), )
    p.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges, minSize=1.0,
                     maxSize=6.0, constraint=FINER)
    p = mdb.models['Model-1'].parts['Part-1']
    e = p.edges
    pickedEndEdges = e.getSequenceFromMask(mask=('[#a ]',), )
    p.seedEdgeByBias(biasMethod=DOUBLE, endEdges=pickedEndEdges, minSize=1.0,
                     maxSize=6.0, constraint=FINER)
    p = mdb.models['Model-1'].parts['Part-1']
    p.generateMesh()
    a = mdb.models['Model-1'].rootAssembly
    a.regenerate()
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    mdb.Job(name='Job-1', model='Model-1', description='pinned sides',
            type=ANALYSIS, atTime=None, waitMinutes=0, waitHours=0, queue=None,
            memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
            explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF,
            modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='',
            scratch='', resultsFormat=ODB)


def make_surface2():
    import section
    import regionToolset
    import displayGroupMdbToolset as dgm
    import part
    import material
    import assembly
    import step
    import interaction
    import load
    import mesh
    import optimization
    import job
    import sketch
    import visualization
    import xyPlot
    import displayGroupOdbToolset as dgo
    import connectorBehavior
    a = mdb.models['Model-1'].rootAssembly
    s1 = a.instances['Part-1-1'].faces
    side2Faces1 = s1.getSequenceFromMask(mask=('[#1 ]',), )
    a.Surface(side2Faces=side2Faces1, name='plate_face')


