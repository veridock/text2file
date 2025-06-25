"""Validator for Markdown files."""

import re
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set, Union

from ...utils.file_utils import is_binary_file, get_file_extension
from ..base import BaseValidator, ValidationResult


class MarkdownValidator(BaseValidator):
    """Validator for Markdown (.md, .markdown) files."""
    
    # Common markdown file extensions
    MARKDOWN_EXTENSIONS = ['md', 'markdown', 'mdown', 'mkd', 'mkdn']
    
    # Common markdown patterns
    HEADER_PATTERN = r'^#{1,6}\s+.+$'
    LIST_PATTERN = r'^[\s]*[-*+]\s+.+$'
    ORDERED_LIST_PATTERN = r'^[\s]*\d+\.\s+.+$'
    CODE_BLOCK_PATTERN = r'```[\s\S]*?```|~~~[\s\S]*?~~~'
    LINK_PATTERN = r'\[([^\]]+)\]\(([^)]+)\)'
    IMAGE_PATTERN = r'!\[([^\]]*)\]\(([^)]+)\)'
    
    @classmethod
    def validate(cls, file_path: Union[str, Path]) -> ValidationResult:
        """Validate that the file is a valid Markdown file.
        
        This checks:
        1. File exists and is readable
        2. File has a valid markdown extension
        3. File is not binary
        4. File contains valid markdown syntax (basic checks)
        
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
        if ext.lower() not in cls.MARKDOWN_EXTENSIONS:
            details['extension'] = ext
            details['expected_extensions'] = cls.MARKDOWN_EXTENSIONS
            return ValidationResult(
                is_valid=False,
                message=f"Invalid file extension for Markdown: {ext}",
                details=details
            )
        
        # Check if file is binary
        if is_binary_file(file_path):
            return ValidationResult(
                is_valid=False,
                message=f"File appears to be a binary file, not Markdown: {file_path}",
                details=details
            )
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
                
            # Check for common markdown patterns
            has_header = bool(re.search(cls.HEADER_PATTERN, content, re.MULTILINE))
            has_list = bool(re.search(cls.LIST_PATTERN, content, re.MULTILINE))
            has_ordered_list = bool(re.search(cls.ORDERED_LIST_PATTERN, content, re.MULTILINE))
            has_code_block = bool(re.search(cls.CODE_BLOCK_PATTERN, content, re.MULTILINE))
            has_link = bool(re.search(cls.LINK_PATTERN, content))
            has_image = bool(re.search(cls.IMAGE_PATTERN, content))
            
            # Check for common markdown elements
            markdown_elements = {
                'headers': has_header,
                'unordered_lists': has_list,
                'ordered_lists': has_ordered_list,
                'code_blocks': has_code_block,
                'links': has_link,
                'images': has_image,
            }
            
            details['markdown_elements'] = markdown_elements
            
            # If no markdown elements are found, it might still be valid but just plain text
            if not any(markdown_elements.values()):
                details['warning'] = "No standard Markdown elements detected. This might be a plain text file."
            
            # Check for common markdown syntax errors
            errors = []
            
            # Check for unclosed code blocks
            code_block_delimiters = re.findall(r'```|~~~', content)
            if len(code_block_delimiters) % 2 != 0:
                errors.append("Unclosed code block detected")
            
            # Check for unclosed links or images
            unclosed_links = re.findall(r'\[[^\]]*$', content, re.MULTILINE)
            unclosed_images = re.findall(r'!\[[^\]]*$', content, re.MULTILINE)
            
            if unclosed_links:
                errors.append(f"Found {len(unclosed_links)} unclosed link(s)")
            if unclosed_images:
                errors.append(f"Found {len(unclosed_images)} unclosed image(s)")
            
            if errors:
                details['errors'] = errors
                return ValidationResult(
                    is_valid=False,
                    message="Markdown validation failed",
                    details=details
                )
            
            return ValidationResult(
                is_valid=True,
                message=f"Valid Markdown file: {file_path}",
                details=details
            )
            
        except (IOError, UnicodeDecodeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Error reading file {file_path}: {str(e)}",
                details=details
            )


# Register the validator
BaseValidator.register_validator('md', MarkdownValidator)
BaseValidator.register_validator('markdown', MarkdownValidator)
BaseValidator.register_validator('mdown', MarkdownValidator)
BaseValidator.register_validator('mkd', MarkdownValidator)
BaseValidator.register_validator('mkdn', MarkdownValidator)
