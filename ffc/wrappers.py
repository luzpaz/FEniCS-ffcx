__author__ = "Anders Logg (logg@simula.no)"
__date__ = "2010-01-18"
__copyright__ = "Copyright (C) 2010 " + __author__
__license__  = "GNU GPL version 3 or any later version"

# Last changed: 2011-03-22

# Python modules
from itertools import chain

# FFC modules
from ffc.log import begin, end, info, error
from ffc.utils import all_equal
from ffc.cpp import format

__all__ = ["generate_wrapper_code"]

# FIXME: More clean-ups needed here.

def generate_wrapper_code(analysis, prefix, parameters):
    "Generate code for additional wrappers."

    # Skip if wrappers not requested
    if not parameters["format"] == "dolfin":
        return None

    # Check that we can import wrappers from dolfin
    try:
        import dolfin_utils.wrappers
    except:
        error("Unable to generate new DOLFIN wrappers, missing module dolfin_utils.wrappers.")

    # Return dolfin wrapper
    return _generate_dolfin_wrapper(analysis, prefix, parameters)

def _generate_dolfin_wrapper(analysis, prefix, parameters):

    begin("Compiler stage 4.1: Generating additional wrapper code")

    # Encapsulate data
    (capsules, common_space) = _encapsulate(prefix, analysis, parameters)

    # Generate code
    info("Generating wrapper code for DOLFIN")
    from dolfin_utils.wrappers import generate_dolfin_code
    code = generate_dolfin_code(prefix, "", capsules, common_space,
                                error_control=parameters["error_control"])
    code += "\n\n"
    end()

    return code

def _encapsulate(prefix, analysis, parameters):

    # Extract data from analysis
    form_datas, elements, element_map = analysis

    num_form_datas = len(form_datas)
    common_space = False

    # Special case: single element
    if num_form_datas == 0:
        capsules = _encapsule_element(prefix, elements)

    # Special case: with error control
    elif (parameters["error_control"] and num_form_datas == 11):
        capsules = [_encapsule_form(prefix, form_data, i, element_map) for
                    (i, form_data) in enumerate(form_datas[:num_form_datas-1])]
        capsules += [_encapsule_form(prefix, form_datas[-1], num_form_datas-1,
                                     element_map, "GoalFunctional")]

    # Otherwise: generate standard capsules for each form
    else:
        capsules = [_encapsule_form(prefix, form_data, i, element_map) for
                    (i, form_data) in enumerate(form_datas)]

        # Check if all elements are equal
        elements = []
        for form_data in form_datas:
            elements += form_data.elements[:form_data.rank]
        common_space = all_equal(elements)

    return (capsules, common_space)


def _encapsule_form(prefix, form_data, i, element_map, superclassname=None):
    element_numbers = [element_map[e] for e in form_data.elements]

    if superclassname is None:
        superclassname = "Form"

    from dolfin_utils.wrappers import UFCFormNames
    form_names = UFCFormNames("%d" % i,
                              form_data.coefficient_names,
                              format["classname form"](prefix, i),
                              [format["classname finite_element"](prefix, j)
                               for j in element_numbers],
                              [format["classname dofmap"](prefix, j)
                               for j in element_numbers],
                              superclassname)
    return form_names

def _encapsule_element(prefix, elements):
    element_number = len(elements) - 1
    args = ("0",
            [format["classname finite_element"](prefix, element_number)],
            [format["classname dofmap"](prefix, element_number)])
    from dolfin_utils.wrappers import UFCElementNames
    return UFCElementNames(*args)
