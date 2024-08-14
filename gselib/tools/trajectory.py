#!/usr/bin/python3
# ----------------------------------------------------------------------------------
# Project: GSELib
# File: trajectory.py
# ----------------------------------------------------------------------------------
# Purpose:
# This file contains the Trajectory dataclass that is used to generate a one-
# dimensional trajectory. The trajectory is generated based on the minimum
# position, maximum position, and step size.
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

from dataclasses import dataclass, field

import numpy as np


@dataclass(frozen=True)
class Trajectory:
    """
    Immutable class for generating a one-dimensional trajectory.

    Attributes:
        min_position: A float representing the minimum position of the trajectory.
        max_position: A float representing the maximum position of the trajectory. Set it to the same value as min_position to generate a single position.
        step: A float representing the step size of the trajectory. Values less than or equal to 0 are considered 0 and counts will be set to 1.
        resolution: An integer representing the number of decimal places to round the positions.

    Example usage:
        trj = Trajectory(min_position=0.0, max_position=10.0, step=1)
        print(trj.position_count)
        print(trj.positions)
        print(trj.positions_reversed)
    """

    min_position: float = field(compare=False)
    max_position: float = field(compare=False)
    step: float = field(compare=False)
    resolution: int = field(compare=False, default=4)

    _position_count: int = field(init=False, compare=False)
    _positions: list[float] = field(default_factory=list, compare=False)

    def __post_init__(self):
        # Set the resolution
        object.__setattr__(self, "min_position", self._set_resolution(self.min_position))
        object.__setattr__(self, "max_position", self._set_resolution(self.max_position))
        object.__setattr__(self, "step", self._set_resolution(self.step))

        # Compute the number of positions
        object.__setattr__(self, "_position_count", self._compute_position_count())

        # Compute the positions
        object.__setattr__(self, "_positions", self._compute_positions())

    def _set_resolution(self, value: float) -> float:
        """Rounds the value to the specified resolution. The default resolution value is 4."""
        if self.resolution < 0:
            raise ValueError("The resolution must be greater than or equal to 0.")
        return float(np.round(value, self.resolution))

    def _compute_position_count(self) -> int:
        """Computes the number of positions based on the min_position, max_position, and step."""
        count = 1

        # Calculate the number of positions when the step is greater than 0
        if self.step > 0:
            count = int(np.round(1 + (np.abs(self.max_position - self.min_position) / np.abs(self.step)), 0))

        return count

    def _compute_positions(self) -> list[float]:
        """Computes the positions based on the min_position, max_position, and step."""
        positions = []

        # Calculate the positions when the position count is not None
        if self._position_count is not None:
            positions = [np.round(step, self.resolution) for step in np.linspace(self.min_position, self.max_position, self._position_count)]

        return positions

    @property
    def position_count(self) -> int:
        """Returns an integer representing the number of positions."""
        return self._position_count

    @property
    def positions(self) -> list[np.float64]:
        """Returns a list of float values representing the positions of the trajectory."""
        return self._positions

    @property
    def positions_reversed(self) -> list[np.float64]:
        """Returns a list of float values representing the positions of the trajectory in reverse order."""
        return self._positions[::-1]
