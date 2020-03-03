# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

from ctypes import c_double, c_int
from mpi4py import MPI
import numpy as np
import pickle
import sys
from lammps import lammps

__author__ = "Jan Janssen"
__copyright__ = (
    "Copyright 2020, Max-Planck-Institut für Eisenforschung GmbH - "
    "Computational Materials Design (CM) Department"
)
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Feb 28, 2020"


# Lammps executable
job = lammps(cmdargs=["-screen", "none"])


def extract_compute(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return np.array(job.extract_compute(*funct_args))


def get_version(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.version()


def get_file(funct_args):
    job.file(*funct_args)


def commands_list(funct_args):
    job.commands_list(*funct_args)


def commands_string(funct_args):
    job.commands_string(*funct_args)


def extract_setting(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.extract_setting(*funct_args)


def extract_global(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.extract_global(*funct_args)


def extract_box(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.extract_box(*funct_args)


def extract_atom(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        #extract atoms return an internal data type
        #this has to be reformatted
        name = str(funct_args[0])
        type = int(funct_args[1])
        val = job.extract_atom(name=name, type=type)
        #this is per atom quantity - so get
        #number of atoms
        natoms = job.get_natoms()
        data = [val[x] for x in range(int(natoms))]
        return data


def extract_fix(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.extract_fix(*funct_args)


def extract_variable(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.extract_variable(*funct_args)


def get_natoms(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.get_natoms()


def set_variable(funct_args):
    return job.set_variable(*funct_args)


def reset_box(funct_args):
    job.reset_box()


def gather_atoms_concat(funct_args):
    return np.array(job.gather_atoms_concat(*funct_args))


def gather_atoms_subset(funct_args):
    return np.array(job.gather_atoms_subset(*funct_args))


def scatter_atoms_subset(funct_args):
    job.scatter_atoms_subset(*funct_args)


def create_atoms(funct_args):
    job.create_atoms(*funct_args)


def has_exceptions(funct_args):
    return job.has_exceptions


def has_gzip_support(funct_args):
    return job.has_gzip_support


def has_png_support(funct_args):
    return job.has_png_support


def has_jpeg_support(funct_args):
    return job.has_jpeg_support


def has_ffmpeg_support(funct_args):
    return job.has_ffmpeg_support


def installed_packages(funct_args):
    return job.installed_packages


def set_fix_external_callback(funct_args):
    job.set_fix_external_callback(*funct_args)


def get_neighlist(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.get_neighlist(*funct_args)


def find_pair_neighlist(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.find_pair_neighlist(*funct_args)


def find_fix_neighlist(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.find_fix_neighlist(*funct_args)


def find_compute_neighlist(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.find_compute_neighlist(*funct_args)


def get_neighlist_size(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.get_neighlist_size(*funct_args)


def get_neighlist_element_neighbors(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return job.get_neighlist_element_neighbors(*funct_args)


def get_thermo(funct_args):
    if MPI.COMM_WORLD.rank == 0:
        return np.array(job.get_thermo(*funct_args))


def scatter_atoms(funct_args):
    py_vector = funct_args[3]
    if issubclass(type(py_vector[0]), np.integer):
        c_vector = (len(py_vector) * c_int)(*py_vector)
    else:
        c_vector = (len(py_vector) * c_double)(*py_vector)
    job.scatter_atoms(funct_args[0], funct_args[1], funct_args[2], c_vector)


def command(funct_args):
    job.command(funct_args)


def gather_atoms(funct_args):
    return np.array(job.gather_atoms(*funct_args))


def select_cmd(argument):
    """
    Select a lammps command

    Args:
        argument (str): [close, extract_compute, get_thermo, scatter_atoms, command, gather_atoms]

    Returns:
        function: the selected function
    """
    switcher = {
        f.__name__: f
        for f in [extract_compute, get_version, get_file, commands_list, commands_string,
                  extract_setting, extract_global, extract_box, extract_atom, extract_fix, extract_variable,
                  get_natoms, set_variable, reset_box, gather_atoms_concat, gather_atoms_subset,
                  scatter_atoms_subset, create_atoms, has_exceptions, has_gzip_support, has_png_support,
                  has_jpeg_support, has_ffmpeg_support, installed_packages, set_fix_external_callback,
                  get_neighlist, find_pair_neighlist, find_fix_neighlist, find_compute_neighlist, get_neighlist_size,
                  get_neighlist_element_neighbors, get_thermo, scatter_atoms, command, gather_atoms]
    }
    return switcher.get(argument)


if __name__ == "__main__":
    while True:
        if MPI.COMM_WORLD.rank == 0:
            input_dict = pickle.load(sys.stdin.buffer)
        else:
            input_dict = None
        input_dict = MPI.COMM_WORLD.bcast(input_dict, root=0)
        if input_dict["c"] == "close":
            job.close()
            break
        output = select_cmd(input_dict["c"])(input_dict["d"])
        if MPI.COMM_WORLD.rank == 0 and output is not None:
            pickle.dump(output, sys.stdout.buffer)
            sys.stdout.flush()
