# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- NURBS manipulated by spreadsheet and numpy
#--
#-- microelly 2016 v 0.1
#-- luzpaz tweaks on 190711
#-- Japp tweaks on 200120 for FreeCAD 0.18:
#--     print() fixed to Python 3
#--     new cellname() column addressable to 702 [A:ZZ]
#--
#-- FreeCAD must have new design file opened, otherwise error:
#--     AttributeError: 'NoneType' object has no attribute 'getObject'
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
#

import numpy as np
import random
import FreeCAD as App
import Part
import Draft


def cellname(col, row):
    ''' Returns spreadsheet cell name for given coordinates (col, row).

    Curently limited to max size of 702 columns,
    i.e. 27x26 2-character combinations.
    '''

    if col > 702:
        raise Exception("Too many spreadsheet columns, use 702 max.")
    F, R = np.divmod(col-1, 26)
    if F == 0:
        cn = chr(R+64+1) + str(row)
    else:
        cn = chr(F+64) + chr(R+64+1) + str(row)
    #print(col, row, cn)
    return cn


def createSpreadsheet(label='Spreadsheet'):
    ''' Creates Spreadsheet in FreeCAD ActiveDocument and filles its headers.
    '''

    ss = App.ActiveDocument.getObject(label)
    if ss == None:
        ss = App.ActiveDocument.addObject('Spreadsheet::Sheet', label)
        ss.set('A1', 'UPoles')
        ss.set('A2', 'VPoles')
        ss.set('A9', 'Poles or Points')
        ss.set('A10', 'u/v and z')
        ss.set('B1', '0')
        ss.setAlias('B1', 'NbUPoles')
        ss.set('B2', '0')
        ss.setAlias('B2', 'NbVPoles')
    return ss


def getSpreadsheet(label='Spreadsheet'):
    return createSpreadsheet(label)

def gendata(spreadsheet, spheremode=False):
        # fill sheet
        ss = spreadsheet

        NbUPoles = 13
        NbVPoles = 17

        if not spheremode:
            # linear model
            x = 200.0*np.array(range(NbUPoles))
            y = 300.0*np.array(range(NbVPoles))
        else:
            #arc model
            x = 360.0/(NbUPoles) * np.array(range(NbUPoles))
            y = 180.0/(NbVPoles) * np.array(range(NbVPoles))
            y -= 90
            x += 180.0/(NbUPoles)
            y += 90.0/(NbVPoles)

        z = 700.0*np.random.random(NbUPoles*NbVPoles)
        z = z.reshape(NbUPoles, NbVPoles)

        ss.set('A1', 'UPoles')
        ss.set('A2', 'VPoles')
        ss.set('A9', 'Poles or Points')
        ss.set('A10', 'u/v and z')

        ss.set('B1', str(NbUPoles))
        ss.setAlias('B1', 'NbUPoles')
        ss.set('B2', str(NbVPoles))
        ss.setAlias('B2', 'NbVPoles')

        for u in range(NbUPoles):
            cn = cellname(u+2, 10)
            ss.set(cn, str(x[u]))

        for v in range(NbVPoles):
            cn = cellname(1, 11+v)
            ss.set(cn, str(y[v]))

        for v in range(NbVPoles):
            for u in range(NbUPoles):
                cn = cellname(u+2, 10+v+1)
                ss.set(cn, str(z[u, v]))

        App.activeDocument().recompute()

def table2array(spreadsheet):
    ''' create array from table'''

    ss = spreadsheet

    NbUPoles = int(ss.NbUPoles)
    NbVPoles = int(ss.NbVPoles)

    x = []
    for u in range(int(ss.NbUPoles)):
        cn = cellname(u+2, 10)
        x.append(ss.get(cn))

    y = []
    for v in range(int(ss.NbVPoles)):
        cn = cellname(1, 11+v)
        y.append(ss.get(cn))

    z = []
    for v in range(NbVPoles):
        for u in range(NbUPoles):
            cn = cellname(u+2, 10+v+1)
            #print(cn)
            z.append(ss.get(cn))

    ps = []
    for v in range(NbVPoles):
        for u in range(NbUPoles):
            p = [x[u], y[v], z[v*NbUPoles+u]]
            #print(p)
            ps.append(p)

    ps = np.array(ps).reshape(NbVPoles, NbUPoles, 3)
    return ps

def tabletop(spreadsheet):
    ''' the first dimension data'''

    ss = spreadsheet

    NbUPoles = int(ss.NbUPoles)
    NbVPoles = int(ss.NbVPoles)

    x = []
    for u in range(int(ss.NbUPoles)):
        cn = cellname(u+2, 10)
        x.append(ss.get(cn))

    return np.array(x)

def tableleft(spreadsheet):
    ''' the 2nd dimension data'''

    ss = spreadsheet

    NbUPoles = int(ss.NbUPoles)
    NbVPoles = int(ss.NbVPoles)

    y = []
    for v in range(int(ss.NbVPoles)):
        cn = cellname(1, 11+v)
        y.append(ss.get(cn))

    return np.array(y)

def setSpreadsheet(ss, x, y, z):

    NbUPoles = len(x)
    NbVPoles = len(y)

    ss.set('B1', str(len(x)))
    ss.set('B2', str(len(y)))

    for u in range(NbUPoles):
        cn = cellname(u+2, 10)
        ss.set(cn, str(x[u]))

    for v in range(NbVPoles):
        cn = cellname(1, 11+v)
        ss.set(cn, str(y[v]))

    for v in range(NbVPoles):
        for u in range(NbUPoles):
            cn = cellname(u+2, 10+v+1)
            ss.set(cn, str(z[u, v]))

    App.activeDocument().recompute()

def table2Nurbs(ss, label="MyNurbs"):
    ''' create nurbs from table'''

    NbUPoles = int(ss.NbUPoles)
    NbVPoles = int(ss.NbVPoles)

    x = []
    for u in range(int(ss.NbUPoles)):
        cn = cellname(u+2, 10)
        x.append(ss.get(cn))

    y = []
    for v in range(int(ss.NbVPoles)):
        cn = cellname(1, 11+v)
        y.append(ss.get(cn))

    z = []
    for v in range(NbVPoles):
        for u in range(NbUPoles):
            cn = cellname(u+2, 10+v+1)
            z.append(ss.get(cn))

    ps = []
    for v in range(NbVPoles):
        for u in range(NbUPoles):
            p = [x[u], y[v], z[v*NbUPoles+u]]
            ps.append(p)

    ps = np.array(ps).reshape(NbVPoles, NbUPoles, 3)

#-hack for 0.16
    ps = []
    for v in range(NbVPoles):
        psl = []
        for u in range(NbUPoles):
            p = (x[u], y[v], z[v*NbUPoles+u])
            psl.append(FreeCAD.Vector(p))
        ps.append(psl)
#- end hack

    bs = Part.BSplineSurface()

    kv = [1.0/(NbVPoles-1)*i for i in range(NbVPoles)]
    ku = [1.0/(NbUPoles-1)*i for i in range(NbUPoles)]

    bs.buildFromPolesMultsKnots(ps,
                    [3] + [1]*(NbVPoles-2) + [3],
                    [3] + [1]*(NbUPoles-2) + [3],
                    kv, ku,
                    False, False,
                    3, 3)

    sha = bs.toShape()
    sp = App.ActiveDocument.addObject("Part::Spline", label)
    sp.Shape = sha
    sp.ViewObject.ControlPoints = True
    sp.ViewObject.ShapeColor = (random.random(), random.random(), random.random())

def array2Nurbs(arr, a, b, c, d, label="MyArrayNurbs", borderPoles=False):
    ''' create nurbs from array'''

    ps = arr[a:a+b, c:c+d]
    NbVPoles, NbUPoles, _t1 = ps.shape

    bs = Part.BSplineSurface()

    if borderPoles:
        kv = [1.0/(NbVPoles-1)*i for i in range(NbVPoles)]
        ku = [1.0/(NbUPoles-1)*i for i in range(NbUPoles)]
        mv = [3] + [1]*(NbVPoles-2) + [3]
        mu = [3] + [1]*(NbUPoles-2) + [3]

        kv= [1.0/(NbVPoles-3)*i for i in range(NbVPoles-2)]
        ku= [1.0/(NbUPoles-3)*i for i in range(NbUPoles-2)]
        mv = [4] + [1]*(NbVPoles-4) + [4]
        mu = [4] + [1]*(NbUPoles-4) + [4]
    else:
        kv = [1.0/(NbVPoles+3)*i for i in range(NbVPoles+4)]
        ku = [1.0/(NbUPoles+3)*i for i in range(NbUPoles+4)]
        mv = [1]*(NbVPoles+4)
        mu = [1]*(NbUPoles+4)

    print (ps.shape, ku, kv)
    bs.buildFromPolesMultsKnots(ps, mv, mu, kv, ku, False, False, 3, 3)

#    bs.insertVKnot(0.51,1,0.0)
#    print "B4xxx5"
# fehler,wenn tolerance kleiner #+# warum bei u=0.2 ??
#    bs.insertUKnot(0.2,1,0.0)
#    bs.insertVKnot(0.2,1,0.0)

    sha = bs.toShape()
    sp = App.ActiveDocument.addObject("Part::Spline", label)
    sp.Shape = sha
    sp.ViewObject.ControlPoints = True
    sp.ViewObject.ShapeColor = (random.random(), random.random(), random.random())
    return sp

def npa2ssa(arr, spreadsheet, c1, r1, color=None):
    ''' write 2s array into spreadsheet '''
    ss = spreadsheet
    arr = np.array(arr)
    try:
        rla, cla = arr.shape
    except:
        rla = arr.shape[0]
        cla = 0
    c2 = c1+cla
    r2 = r1+rla
    #print("update ss -------------  xxx")
    #print(arr)
    #print((c1, r1, cla))

    if cla == 0:
        for r in range(r1, r2):
            cn = cellname(c1, r)
            ss.set(cn, str(arr[r-r1]))
            if color != None: ss.setBackground(cn, color)
    else:
        for r in range(r1, r2):
            for c in range(c1, c2):
                cn=cellname(c, r)
                #print((cn, c, r, arr[r-r1, c-c1]))
                ss.set(cn, str(arr[r-r1, c-c1]))
                #print(("!!", cn, c, r, arr[r-r1, c-c1], ss.get(cn)))
                if color != None: ss.setBackground(cn, color)

def ssa2npa(spreadsheet, c1, r1, c2, r2, default=None):
    ''' create array from table'''

    c2 += 1
    r2 += 1

    ss = spreadsheet
    z = []
    for r in range(r1, r2):
        for c in range(c1, c2):
            cn=cellname(c, r)
            # print cn
            try:
                v = ss.get(cn)
                z.append(ss.get(cn))
            except:
                z.append(default)


    z = np.array(z)
    #print(z)
    ps = np.array(z).reshape(r2-r1, c2-c1)
    return ps

#-----------------------------------
# test case

if 0 and __name__=='__main__':
    ss1=createSpreadsheet(label='MySpreadsheet')
    w = 4.0
    x = np.linspace(-w, w, 25)
    y = np.linspace(-w, w, 25)
    xx, yy = np.meshgrid(x, y)
    z = np.sin(xx**2+yy**2)
    setSpreadsheet(ss1, x, y, z)
    table2Nurbs(ss1, "Test_Surf")

