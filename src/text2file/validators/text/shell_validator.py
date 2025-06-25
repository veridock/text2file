"""Validator for shell script files."""

import os
import re
import subprocess
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from ...utils.file_utils import get_file_extension, is_binary_file
from ..base import BaseValidator, ValidationResult


class ShellScriptValidator(BaseValidator):
    """Validator for shell script (.sh) files."""

    # Common shell script shebangs
    SHELL_SHEBANGS = [
        "#!/bin/sh",
        "#!/bin/bash",
        "#!/bin/zsh",
        "#!/bin/ksh",
        "#!/bin/dash",
        "#!/usr/bin/env bash",
        "#!/usr/bin/env sh",
        "#!/usr/bin/env zsh",
        "#!/usr/bin/env ksh",
        "#!/usr/bin/env dash",
    ]

    # Common shell script file extensions
    SHELL_EXTENSIONS = ["sh", "bash", "zsh", "ksh", "csh", "fish"]

    def _parse_shebang(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse the shebang line from shell script content.
        
        Args:
            content: The shell script content
            
        Returns:
            Tuple of (interpreter, path) if shebang found, (None, None) otherwise
        """
        if not content.startswith('#!'):
            return None, None
            
        shebang_line = content.split('\n', 1)[0].strip()
        parts = shebang_line[2:].strip().split()
        
        if not parts:
            return None, None
            
        interpreter = parts[0]
        path = parts[1] if len(parts) > 1 else None
        
        return interpreter, path

    def _run_shellcheck(self, filepath: Path) -> Tuple[bool, str]:
        """Run shellcheck on the shell script.
        
        Args:
            filepath: Path to the shell script
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not shutil.which('shellcheck'):
            return False, "shellcheck is not installed"
            
        try:
            result = subprocess.run(
                ['shellcheck', str(filepath)],
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                return True, "Shellcheck validation passed"
            else:
                return False, f"Shellcheck validation failed: {result.stderr}"
                
        except Exception as e:
            return False, f"Error running shellcheck: {str(e)}"

    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> ValidationResult:
        """Validate that the file is a valid shell script.

        This checks:
        1. File exists and is readable
        2. File has a valid shell script extension
        3. File starts with a valid shebang (optional but recommended)
        4. File can be parsed by shellcheck (if available)

        Args:
            file_path: Path to the file to validate

        Returns:
            ValidationResult indicating whether the file is valid
        """
        file_path = Path(file_path)
        details: Dict[str, Any] = {}

        # Check if file exists
        if not file_path.exists():
            return ValidationResult(
                is_valid=False,
                message=f"File does not exist: {file_path}",
                details=details,
            )

        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return ValidationResult(
                is_valid=False,
                message=f"File is not readable: {file_path}",
                details=details,
            )

        # Check file extension
        ext = get_file_extension(file_path)
        if ext.lower() not in cls.SHELL_EXTENSIONS:
            details["extension"] = ext
            details["expected_extensions"] = cls.SHELL_EXTENSIONS

        # Check if file is binary
        if is_binary_file(file_path):
            return ValidationResult(
                is_valid=False,
                message=f"File appears to be a binary file, not a shell script: {file_path}",
                details=details,
            )

        # Read first few lines to check for shebang
        has_shebang = False
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline().strip()

                # Check for shebang
                if first_line.startswith("#!") and any(
                    first_line.startswith(shebang) for shebang in cls.SHELL_SHEBANGS
                ):
                    has_shebang = True
                    details["shebang"] = first_line
                else:
                    # Check if it's a valid shell script without shebang (allowed but not recommended)
                    details[
                        "warning"
                    ] = "No valid shebang found. While shell scripts can run without a shebang, it's recommended to include one."

                # Read more lines to check for common shell script patterns
                content = first_line + "\n" + f.read(4096)  # Read first 4KB

                # Check for common shell script patterns
                shell_patterns = [
                    r"\b(if|then|else|fi|for|do|done|while|until|case|esac|function)\b",
                    r"\b(echo|printf|read|export|local|declare|typeset|readonly)\b",
                    r"\$\{[^}]+\}",  # ${variable}
                    r"\$[a-zA-Z_][a-zA-Z0-9_]*",  # $variable
                    r"`.*`",  # Command substitution
                    r"\$\(.*\)",  # $(command substitution)
                ]

                pattern_matches = 0
                for pattern in shell_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        pattern_matches += 1

                if (
                    pattern_matches < 2
                ):  # Require at least 2 shell patterns to be somewhat confident
                    details[
                        "warning"
                    ] = "File doesn't appear to contain common shell script patterns"

        except (IOError, UnicodeDecodeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error reading file {file_path}: {str(e)}",
                details=details,
            )

        # Run shellcheck if available
        is_valid, message = cls._run_shellcheck(file_path)
        if not is_valid:
            details["shellcheck_output"] = message
            return ValidationResult(
                is_valid=False,
                message=f"Shell script validation failed ({message})",
                details=details,
            )
        else:
            details[
                "info"
            ] = "shellcheck is not installed. Install it for more thorough validation."

        # If we got here, the file is valid
        return ValidationResult(
            is_valid=True, message=f"Valid shell script: {file_path}", details=details
        )


# Register the validator
BaseValidator.register_validator("sh", ShellScriptValidator)
BaseValidator.register_validator("bash", ShellScriptValidator)
BaseValidator.register_validator("zsh", ShellScriptValidator)
BaseValidator.register_validator("ksh", ShellScriptValidator)
BaseValidator.register_validator("csh", ShellScriptValidator)
BaseValidator.register_validator("fish", ShellScriptValidator)
