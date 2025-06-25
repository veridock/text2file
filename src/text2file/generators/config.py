"""Configuration file generators."""

import json
import os
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from rich.prompt import Prompt

from ..generators.base import BaseGenerator
from ..generators.registration import register_generator_directly


def _parse_config_content(content: str) -> Dict[str, Any]:
    """Parse configuration content into a dictionary.
    
    Args:
        content: Configuration content in JSON, YAML, or INI format
        
    Returns:
        Parsed configuration as a dictionary
        
    Raises:
        ValueError: If the content cannot be parsed
    """
    import logging
    
    # Debug log the original content
    logging.debug(f"Original content: {content!r}")
    
    content = content.strip()
    if not content:
        logging.debug("Empty content after strip, returning empty dict")
        return {}
    
    # Clean up the content by normalizing indentation
    lines = content.splitlines()
    if lines:
        # Remove common indentation
        content = textwrap.dedent(content)
        logging.debug(f"Content after dedent: {content!r}")
    
    # Try parsing as JSON first (most specific check)
    content_stripped = content.strip()
    if content_stripped.startswith('{') or content_stripped.startswith('['):
        try:
            result = json.loads(content_stripped)
            logging.debug(f"Successfully parsed as JSON: {result!r}")
            return result
        except json.JSONDecodeError as e:
            logging.debug(f"JSON parsing failed: {e}")
    
    # Try parsing as YAML
    try:
        logging.debug("Trying to parse as YAML")
        # First try with safe_load
        result = yaml.safe_load(content)
        logging.debug(f"Result from yaml.safe_load: {result!r}")
        
        # If we got None but content isn't empty, try with full_load
        if result is None and content_stripped:
            logging.debug("Trying yaml.full_load")
            result = yaml.full_load(content)
            logging.debug(f"Result from yaml.full_load: {result!r}")
            
        if result is not None:  # Only return if we got a valid result
            return result
            
    except (yaml.YAMLError, AttributeError) as e:
        logging.debug(f"YAML parsing error: {e}")
    
    # If we get here, try parsing as INI-style
    logging.debug("Falling back to INI parsing")
        
    # If we get here, try parsing as INI-style
    config = {}
    current_section = None
    
    for line in content.split('\n'):
        line = line.strip()
        if not line or line.startswith(';'):
            continue
            
        # Handle section headers
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1].strip()
            config[current_section] = {}
            continue
            
        # Handle key-value pairs
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()
            
            # Try to convert value to appropriate type
            if value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value.isdigit():
                value = int(value)
            else:
                try:
                    value = float(value)
                except ValueError:
                    pass
                    
            if current_section is not None:
                config[current_section][key] = value
            else:
                config[key] = value
                
    return config


def _generate_yaml(config: Dict[str, Any]) -> str:
    """Generate YAML from a configuration dictionary."""
    return yaml.dump(config, default_flow_style=False, sort_keys=False)


def _generate_toml(config: Dict[str, Any]) -> str:
    """Generate TOML from a configuration dictionary."""
    try:
        import toml
        return toml.dumps(config)
    except ImportError:
        # Fall back to a simple TOML-like format
        lines = []
        for key, value in config.items():
            if isinstance(value, dict):
                lines.append(f"[{key}]")
                for k, v in value.items():
                    lines.append(f"{k} = {_format_toml_value(v)}")
                lines.append("")
            else:
                lines.append(f"{key} = {_format_toml_value(value)}")
        return "\n".join(lines)


def _format_toml_value(value: Any) -> str:
    """Format a value for TOML output."""
    if isinstance(value, str):
        return f'"{value}"'
    elif isinstance(value, bool):
        return str(value).lower()
    return str(value)


def _generate_ini(config: Dict[str, Any]) -> str:
    """Generate INI from a configuration dictionary."""
    lines = []
    
    # Handle top-level keys first
    for key, value in config.items():
        if not isinstance(value, dict):
            lines.append(f"{key} = {value}")
    
    # Handle sections
    for section, options in config.items():
        if isinstance(options, dict):
            lines.append(f"\n[{section}]")
            for key, value in options.items():
                lines.append(f"{key} = {value}")
                
    return "\n".join(lines)


class ConfigGenerator(BaseGenerator):
    """Generator for configuration files.
    
    This generator can convert between different configuration file formats including
    JSON, YAML, TOML, and INI. It automatically detects the input format and can
    convert to any of the supported output formats.
    """
    
    @classmethod
    def generate(
        cls,
        content: str,
        output_path: Union[str, Path],
        **kwargs: Any
    ) -> Path:
        """Generate a configuration file.
        
        Args:
            content: Configuration content (JSON, YAML, or INI format)
            output_path: Path to write the configuration file to
            **kwargs: Additional keyword arguments including:
                format: Output format (yaml, toml, ini, json). Defaults to 'yaml'.
                
        Returns:
            Path to the generated file
            
        Raises:
            ValueError: If the format is not supported or content cannot be parsed
            IOError: If there's an error writing the file
        """
        output_path = Path(output_path)
        format = kwargs.get('format', 'yaml').lower()
        
        # Parse the input content
        config = _parse_config_content(content)
        
        # Generate the output in the requested format
        format = format.lower()
        if format in ("yaml", "yml"):
            output = _generate_yaml(config)
            ext = ".yaml"
        elif format == "toml":
            output = _generate_toml(config)
            ext = ".toml"
        elif format == "ini":
            output = _generate_ini(config)
            ext = ".ini"
        elif format == "json":
            output = json.dumps(config, indent=2)
            ext = ".json"
        else:
            raise ValueError(f"Unsupported config format: {format}")
        
        # Ensure the output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the output file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(output)
            
        return output_path


# Register the generator for different config file formats
register_generator_directly(
    ["yaml", "yml"],
    lambda content, path, **kw: ConfigGenerator.generate(content, path, format="yaml", **kw)
)

register_generator_directly(
    ["toml"],
    lambda content, path, **kw: ConfigGenerator.generate(content, path, format="toml", **kw)
)

register_generator_directly(
    ["ini", "cfg", "conf"],
    lambda content, path, **kw: ConfigGenerator.generate(content, path, format="ini", **kw)
)

# Also register JSON since we support it as an output format
register_generator_directly(
    ["json"],
    lambda content, path, **kw: ConfigGenerator.generate(content, path, format="json", **kw)
)
