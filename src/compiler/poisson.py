name = "MyPDE"
from form import *
    
dx = Integral("interior")
ds = Integral("boundary")

# Copyright (c) 2004 Anders Logg (logg@tti-c.org)
# Licensed under the GNU GPL Version 2
#
# The bilinear form for Poisson's equation.
# Compile this form with FFC.

name = "Poisson"
element = FiniteElement("Lagrange", 1, "triangle")

u = BasisFunction(element)
v = BasisFunction(element)
i = Index()
    
a = u.dx(i)*v.dx(i)*dx + u*v*ds

form = Form(a, name)
form.compile("")
