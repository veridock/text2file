"""Validator for shell script files."""

import re
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from ...utils.file_utils import is_binary_file, get_file_extension
from ..base import BaseValidator, ValidationResult


class ShellScriptValidator(BaseValidator):
    """Validator for shell script (.sh) files."""
    
    # Common shell script shebangs
    SHELL_SHEBANGS = [
        '#!/bin/sh',
        '#!/bin/bash',
        '#!/bin/zsh',
        '#!/bin/ksh',
        '#!/bin/dash',
        '#!/usr/bin/env bash',
        '#!/usr/bin/env sh',
        '#!/usr/bin/env zsh',
        '#!/usr/bin/env ksh',
        '#!/usr/bin/env dash',
    ]
    
    # Common shell script file extensions
    SHELL_EXTENSIONS = ['sh', 'bash', 'zsh', 'ksh', 'csh', 'fish']
    
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
                details=details
            )
        
        # Check if file is readable
        if not os.access(file_path, os.R_OK):
            return ValidationResult(
                is_valid=False,
                message=f"File is not readable: {file_path}",
                details=details
            )
        
        # Check file extension
        ext = get_file_extension(file_path)
        if ext.lower() not in cls.SHELL_EXTENSIONS:
            details['extension'] = ext
            details['expected_extensions'] = cls.SHELL_EXTENSIONS
        
        # Check if file is binary
        if is_binary_file(file_path):
            return ValidationResult(
                is_valid=False,
                message=f"File appears to be a binary file, not a shell script: {file_path}",
                details=details
            )
        
        # Read first few lines to check for shebang
        has_shebang = False
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                
                # Check for shebang
                if first_line.startswith('#!') and any(
                    first_line.startswith(shebang) 
                    for shebang in cls.SHELL_SHEBANGS
                ):
                    has_shebang = True
                    details['shebang'] = first_line
                else:
                    # Check if it's a valid shell script without shebang (allowed but not recommended)
                    details['warning'] = "No valid shebang found. While shell scripts can run without a shebang, it's recommended to include one."
                    
                # Read more lines to check for common shell script patterns
                content = first_line + '\n' + f.read(4096)  # Read first 4KB
                
                # Check for common shell script patterns
                shell_patterns = [
                    r'\b(if|then|else|fi|for|do|done|while|until|case|esac|function)\b',
                    r'\b(echo|printf|read|export|local|declare|typeset|readonly)\b',
                    r'\$\{[^}]+\}',  # ${variable}
                    r'\$[a-zA-Z_][a-zA-Z0-9_]*',  # $variable
                    r'`.*`',  # Command substitution
                    r'\$\(.*\)',  # $(command substitution)
                ]
                
                pattern_matches = 0
                for pattern in shell_patterns:
                    if re.search(pattern, content, re.MULTILINE):
                        pattern_matches += 1
                
                if pattern_matches < 2:  # Require at least 2 shell patterns to be somewhat confident
                    details['warning'] = "File doesn't appear to contain common shell script patterns"
                
        except (IOError, UnicodeDecodeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error reading file {file_path}: {str(e)}",
                details=details
            )
        
        # Run shellcheck if available
        shellcheck_available = shutil.which('shellcheck') is not None
        if shellcheck_available:
            try:
                result = subprocess.run(
                    ['shellcheck', '-x', str(file_path)],
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    details['shellcheck_output'] = result.stderr or result.stdout
                    details['shellcheck_returncode'] = result.returncode
                    
                    return ValidationResult(
                        is_valid=False,
                        message=f"Shell script validation failed (shellcheck returned {result.returncode})",
                        details=details
                    )
                
            except (subprocess.SubprocessError, OSError) as e:
                details['shellcheck_error'] = str(e)
        else:
            details['info'] = "shellcheck is not installed. Install it for more thorough validation."
        
        # If we got here, the file is valid
        return ValidationResult(
            is_valid=True,
            message=f"Valid shell script: {file_path}",
            details=details
        )


# Register the validator
BaseValidator.register_validator('sh', ShellScriptValidator)
BaseValidator.register_validator('bash', ShellScriptValidator)
BaseValidator.register_validator('zsh', ShellScriptValidator)
BaseValidator.register_validator('ksh', ShellScriptValidator)
BaseValidator.register_validator('csh', ShellScriptValidator)
BaseValidator.register_validator('fish', ShellScriptValidator)
