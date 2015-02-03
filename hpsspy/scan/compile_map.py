# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def compile_map(old_map,release):
    """Compile the regular expressions in a map.

    Parameters
    ----------
    old_map : dict
        A dictionary containing regular expressions to compile.
    release : str
        An initial key to determine the section of the dictionary of interest.

    Returns
    -------
    compile_map : dict
        A new dictionary containing compiled regular expressions.
    """
    from re import compile
    new_map = dict()
    for key in old_map[release]:
        if key == 'exclude':
            new_map[key] = frozenset(old_map[release][key])
        else:
            foo = list()
            for r in old_map[release][key]:
                foo.append((compile(r),old_map[release][key][r]))
            new_map[key] = tuple(foo)
    return new_map
