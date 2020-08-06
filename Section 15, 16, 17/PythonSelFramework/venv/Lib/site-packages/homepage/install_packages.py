#!/usr/bin/env python3

import platform
from pathlib import Path
from subprocess import CalledProcessError, check_call  # noqa: S404
from typing import List, Union


class OSInteractionLayer():
    """Detects package manager used by system and attempts to install HomePage dependencies."""

    def __init__(self) -> None:
        self.IS_WINDOWS: bool = (platform.system().lower() == "windows")

    def __get_distro(self) -> bool:
        """Get the OS-release"""

        if not(self.IS_WINDOWS):
            with open(Path("/etc/os-release"), "r") as RELEASE_FILE:
                self.OS_RELEASE: Union[List[str], str] = RELEASE_FILE.read().split("\n")
            self.OS_RELEASE = sum([i.split("=") for i in self.OS_RELEASE], [])
            self.OS_RELEASE = self.OS_RELEASE[self.OS_RELEASE.index("ID") + 1].strip('"').lower()
            return True

        else:
            return False

    def is_prog_present(self, pkg_mgr_name: str) -> bool:
        checker_cmd: str = ('/usr/bin/env bash -c '
                            f'"hash {pkg_mgr_name} '
                            '>/dev/null 2>/dev/null '
                            f'|| command -v {pkg_mgr_name} '
                            '>/dev/null 2>/dev/null"'
                            )
        try:
            return not bool(
                check_call(checker_cmd, shell=True)  # noqa: S602
            )
        except(CalledProcessError):
            return False

    def __install_nix_pkg(self) -> bool:
        """Determine package manager and install packages required."""

        try:
            for name, actions in self.package_mapping.items():
                if self.is_prog_present(name):
                    for pkg_mgr_cmd in actions:
                        check_call(f"{pkg_mgr_cmd}", shell=True)  # noqa: S602
                    else:
                        return True
            else:
                return False

        except(CalledProcessError, KeyboardInterrupt):
            return False

    def __install_win_pkg(self) -> bool:
        """Install the windows packages. Not added yet."""

        return False

    def install_packages(self, **package_mapping) -> bool:
        self.package_mapping = package_mapping

        if not self.IS_WINDOWS:
            return self.__install_nix_pkg()

        else:
            return self.__install_win_pkg()

    def compile_dist_pkg(self, **dist_mapping) -> bool:
        """Compile source packages, discriminate based on os-release"""

        try:
            if self.__get_distro():
                for rel_actual_name, actions in dist_mapping.items():
                    if self.OS_RELEASE == rel_actual_name:
                        for compile_instruction in actions[1:]:
                            check_call(f"{compile_instruction}", shell=True)  # noqa: S602
                        else:
                            return True
                else:
                    for actions in dist_mapping.values():
                        if self.is_prog_present(actions[0]):
                            print(f"Distro not found, using fallback based on {actions[0]}")
                            for compile_instruction in actions[1:]:
                                check_call(f"{compile_instruction}", shell=True)  # noqa: S602
                            else:
                                return True
                    else:
                        print("Unable to match supported distro or package manager.")
                        print("Please file an issue with your /etc/os-release file and package manager.")
                        return False

            return False

        except(CalledProcessError, KeyboardInterrupt):
            return False
