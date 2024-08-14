#!/usr/bin/python3
# ----------------------------------------------------------------------------------
# Project: GSELib
# File: maps.py
# ----------------------------------------------------------------------------------
# Purpose:
# This file contains the BaseMap and Map dataclasses that are used to generate a
# 1D, 2D, or 3D map. The map is generated making use of the Trajectory dataclass.
# ----------------------------------------------------------------------------------
# Author: Christofanis Skordas
#
# Copyright (C) 2024 GSECARS, The University of Chicago, USA
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ----------------------------------------------------------------------------------

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np

from gselib.tools.trajectory import Trajectory


@dataclass(frozen=True)
class BaseMap(ABC):

    _position_count: int = field(init=False, repr=False, compare=False)
    _position_list: np.array = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        # Calculate the number of positions for the map
        object.__setattr__(self, "_position_count", self._calculate_position_count())

        # Set the position list
        object.__setattr__(self, "_position_list", self._calculate_position_list())

    @abstractmethod
    def _calculate_position_count(self) -> int:
        """Returns the total number of points for the map."""

    @abstractmethod
    def _calculate_position_list(self) -> np.array:
        """Generates an n-dimensional array with all the map positions."""

    @property
    def position_count(self) -> int:
        return self._position_count

    @property
    def positions(self) -> np.array:
        return self._position_list


@dataclass(frozen=True)
class Map1D(BaseMap):

    trj_linear: Trajectory = field(compare=False)

    def _calculate_position_count(self) -> int:
        return self.trj_linear.position_count

    def _calculate_position_list(self) -> np.array:
        return np.array(self.trj_linear.positions)


@dataclass(frozen=True)
class Map2D(BaseMap):

    trj_x: Trajectory = field(compare=False)
    trj_y: Trajectory = field(compare=False)

    def _calculate_position_count(self) -> int:
        return self.trj_x.position_count * self.trj_y.position_count

    def _calculate_position_list(self) -> np.array:
        return np.array(np.meshgrid(self.trj_x.positions, self.trj_y.positions)).T.reshape(-1, 2)


@dataclass(frozen=True)
class Map3D(BaseMap):

    trj_x: Trajectory = field(compare=False)
    trj_y: Trajectory = field(compare=False)
    trj_z: Trajectory = field(compare=False)

    def _calculate_position_count(self) -> int:
        return self.trj_x.position_count * self.trj_y.position_count * self.trj_z.position_count

    def _calculate_position_list(self) -> np.array:
        return np.array(np.meshgrid(self.trj_x.positions, self.trj_y.positions, self.trj_z.positions)).T.reshape(-1, 3)
