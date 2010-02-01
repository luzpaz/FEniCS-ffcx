#!/usr/bin/env python

__author__ = "Kristian B. Oelgaard (k.b.oelgaard@gmail.com)"
__date__ = "2010-01-06"
__copyright__ = "Copyright (C) 2010 Kristian B. Oelgaard"
__license__  = "GNU GPL version 3 or any later version"

# Last changed: 2010-02-01

# Pyhton modules
import unittest
import time

# FFC modules
from ffc.quadrature.symbolics import *
from ffc.cpp import format, set_float_formatting
from ffc.parameters import FFC_PARAMETERS
set_float_formatting(FFC_PARAMETERS['precision'])

class TestReduceVarType(unittest.TestCase):

    def testReduceVarType(self):
        f1 = FloatValue(1)
        f2 = FloatValue(2)
        f3 = FloatValue(3)
        f5 = FloatValue(5)
        fm4 = FloatValue(-4)

        B0 = Symbol("B0",BASIS)
        B1 = Symbol("B1", BASIS)
        Bm4 = Product([fm4, B1])
        B5 = Product([f5, B0])

        I0 = Symbol("I0", IP)
        I1 = Symbol("I1", IP)
        I5 = Product([f5, I0])

        G0 = Symbol("G0", GEO)
        G3 = Product([f3, G0])


        C0 = Symbol("C0", CONST)
        C2 = Product([f2, C0])

        p0 = Product([B0,I5])
        p1 = Product([B0,B1])

        S0 = Sum([B0, I5])
        S1 = Sum([p0, p1])
        S2 = Sum([B0, B1])
        S3 = Sum([B0, p0])
        S4 = Sum([f5, p0])

        F0 = Fraction(B0,I5).expand()
        F1 = Fraction(p1,I5).expand()
        F2 = Fraction(G3,S2).expand()
        F3 = Fraction(G3,S3).expand()
        F4 = Fraction(I1, Sum([I1, I0]))

        r0 = B0.reduce_vartype(BASIS)
        r1 = B0.reduce_vartype(CONST)

        rp0 = p0.reduce_vartype(BASIS)
        rp1 = p0.reduce_vartype(IP)
        rp2 = p1.reduce_vartype(BASIS)
        rp3 = p1.reduce_vartype(GEO)

        rs0 = S0.reduce_vartype(BASIS)
        rs1 = S0.reduce_vartype(IP)
        rs2 = S1.reduce_vartype(BASIS)
        rs3 = S4.reduce_vartype(BASIS)
        rs4 = S4.reduce_vartype(CONST)

        rf0 = F0.reduce_vartype(BASIS)
        rf1 = F1.reduce_vartype(BASIS)
        rf2 = F0.reduce_vartype(IP)
        rf3 = F2.reduce_vartype(BASIS)
        rf4 = F3.reduce_vartype(BASIS)
        rf5 = F4.reduce_vartype(IP)

#        print
#        print "%s, red(BASIS): ('%s', '%s')" %(B0, r0[0], r0[1])
#        print "%s, red(CONST): ('%s', '%s')" %(B0, r1[0], r1[1])

#        print "\n%s, red(BASIS): ('%s', '%s')" %(p0, rp0[0], rp0[1])
#        print "%s, red(IP):    ('%s', '%s')" %(p0, rp1[0], rp1[1])
#        print "%s, red(BASIS): ('%s', '%s')" %(p1, rp2[0], rp2[1])
#        print "%s, red(CONST): ('%s', '%s')" %(p1, rp3[0], rp3[1])

#        print "\n%s, red(BASIS): ('%s', '%s')" %(S0, rs0[0], rs0[1])
#        print "%s, red(IP):    ('%s', '%s')" %(S0, rs1[0], rs1[1])
#        print "%s, red(BASIS): '%s', '%s'" %(S1, rs2[0], rs2[1])
#        print "%s, red(BASIS): '%s', '%s'" %(S4, rs3[0], rs3[1])
#        print "%s, red(BASIS): '%s'" %(S4, rs4[0])

#        print "\nrf0: %s, red(BASIS): ('%s', '%s')" %(F0, rf0[0], rf0[1])
#        print "rf1: %s, red(BASIS): ('%s', '%s')" %(F1, rf1[0], rf1[1])
#        print "rf2: %s, red(IP): ('%s', '%s')" %(F0, rf2[0], rf2[1])
#        print "rf3: %s, red(BASIS): ('%s', '%s')" %(F2, rf3[0], rf3[1])
#        print "rf4: %s, red(BASIS): ('%s', '%s')" %(F3, rf4[0], rf4[1])
#        print "rf5: %s, red(IP): ('%s', '%s')" %(F4, rf5[0], rf5[1])

        self.assertEqual((B0, f1), r0)
        self.assertEqual(((), B0), r1)

        self.assertEqual((B0, I5), rp0)
        self.assertEqual((I0, B5),  rp1)
        self.assertEqual((p1, f1), rp2)
        self.assertEqual(((), p1),  rp3)

        self.assertEqual(((), I5), rs0[0])
        self.assertEqual((B0, f1), rs0[1])
        self.assertEqual((I0, f5), rs1[0])
        self.assertEqual(((), B0), rs1[1])
        self.assertEqual((
        Product([B0, B1]), f1), rs2[0])
        self.assertEqual((B0, I5), rs2[1])
        self.assertEqual(((), f5), rs3[0])
        self.assertEqual((B0, I5), rs3[1])
        self.assertEqual((f5,
        Sum([f1,
        Product([B0, I0])])), rs4[0])

        self.assertEqual((B0, Fraction(FloatValue(0.2), I0)), rf0)
        self.assertEqual((
        Product([B0, B1]), Fraction(FloatValue(0.2), I0)), rf1)
        self.assertEqual( ( Fraction(f1, I0),
        Product([FloatValue(0.2), B0]) ), rf2)
        self.assertEqual((Fraction(f1, S2), G3), rf3)
        self.assertEqual( ( Fraction(f1, B0), Fraction( G3, Sum([I5, f1]))), rf4)
        self.assertEqual(F4, rf5[0])
        self.assertEqual(FloatValue(1), rf5[1])

if __name__ == "__main__":

    # Run all returned tests
    runner = unittest.TextTestRunner()
    runner.run(TestReduceVarType('testReduceVarType'))

