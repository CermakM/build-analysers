#!/usr/bin/env python3
# thoth-build-analysers
# Copyright(C) 2018, 2019 Marek Cermak
#
# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>

"""Command line interface for Thoth build-analysers library."""

import fire
import json

from functools import wraps

from pathlib import Path
from prettyprinter import pformat
from typing import Union

from thoth.build_analysers.preprocessing import build_log_to_dependency_table

from thoth.build_analysers.analysis import build_breaker_analyze
from thoth.build_analysers.analysis import build_breaker_report

from thoth.build_analysers.analysis import get_failed_branch
from thoth.build_analysers.analysis import get_succesfully_installed_packages


def doc(parent: callable):

    docstring: str = parent.__doc__

    @wraps(parent)
    def inner_decorator(func):

        func.__doc__ = docstring
        return func
    
    return inner_decorator



class CLI(object):

    def __init__(self, verbose: bool = False, pretty: bool = False):
        self.log = None

        self.verbose: bool = verbose
        self.pretty: bool = pretty

    @doc(build_breaker_report)
    def report(
        self,
        log: Union[str, Path],
        candidates: bool = True,
        top: int = 5,
        handler: str = None,
        colorize: bool = False,
    ) -> str:
        with open(log, 'r') as f:
            self.log: str = f.read()

        result: dict = build_breaker_report(log=self.log, handler=handler, top=top, colorize=colorize)

        if not candidates:
            result.pop("candidates")

        if self.pretty:
            result: str = pformat(result)

            return result
        
        return json.dumps(result)
    
    @doc(build_breaker_analyze)
    def analyse(self, log: Union[str, Path], output: str = "plain") -> str:
        with open(log, 'r') as f:
            self.log: str = f.read()
        
        _, df = build_breaker_analyze(self.log)

        return self._format_table(df)

    @doc(build_breaker_analyze)
    def analyze(self, log:Union[str, Path], output: str = "plain") -> str:
        return analyse(log=log, output=output)  # alias to `analyse`
    
    @doc(build_log_to_dependency_table)
    def dependencies(self, log: Union[str, Path], output: str = "plain"):
        with open(log, 'r') as f:
            self.log: str = f.read()

        df = build_log_to_dependency_table(self.log)

        return self._format_table(df, output)

    def _format_table(self, df, output: str = "plain") -> str:
        """Format pandas DataFrame for console output."""
        if output is "plain":
            result: str = pformat(df)

            return result

        elif output in ("json", "dict"):
            result: str = df.to_dict(orient="records")
        elif output is "records":
            result: list = df.to_records().tolist()
        else:
            result = eval(f"df.to_{output}()")
        
        if self.pretty:
            result: str = pformat(result)

            return result
        
        return json.dumps(result)


if __name__ == "__main__":
    fire.Fire(CLI)
