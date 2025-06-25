"""Tests for the configuration file generator."""

import json
import os
from pathlib import Path
import tempfile
import unittest

import yaml

try:
    import tomli as toml
except ImportError:
    import toml

from text2file.generators.config import (
    _parse_config_content,
    _generate_yaml,
    _generate_toml,
    _generate_ini,
    ConfigGenerator,
)


class TestConfigGenerator(unittest.TestCase):
    """Test the config generator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.test_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "testdb",
                "enabled": True,
            },
            "server": {
                "host": "0.0.0.0",
                "port": 8000,
                "debug": True,
            },
            "features": ["auth", "logging", "caching"],
        }
        self.test_config_str = json.dumps(self.test_config, indent=2)

    def test_parse_json_content(self):
        """Test parsing JSON config content."""
        content = '{"key": "value", "nested": {"num": 42}}'
        result = _parse_config_content(content)
        self.assertEqual(result, {"key": "value", "nested": {"num": 42}})

    def test_parse_yaml_content(self):
        """Test parsing YAML config content."""
        content = """
        key: value
        nested:
          num: 42
          enabled: true
        """
        result = _parse_config_content(content)
        self.assertEqual(result, {"key": "value", "nested": {"num": 42, "enabled": True}})

    def test_parse_ini_content(self):
        """Test parsing INI-style config content."""
        content = """
        [section1]
        key1 = value1
        key2 = 42
        key3 = true
        
        [section2]
        key4 = value4
        """
        result = _parse_config_content(content)
        self.assertEqual(
            result,
            {
                "section1": {"key1": "value1", "key2": 42, "key3": True},
                "section2": {"key4": "value4"},
            },
        )

    def test_generate_yaml(self):
        """Test YAML generation."""
        yaml_str = _generate_yaml(self.test_config)
        parsed = yaml.safe_load(yaml_str)
        self.assertEqual(parsed, self.test_config)

    def test_generate_toml(self):
        """Test TOML generation."""
        toml_str = _generate_toml(self.test_config)
        parsed = toml.loads(toml_str)
        self.assertEqual(parsed["database"]["port"], 5432)
        self.assertEqual(parsed["server"]["debug"], True)

    def test_generate_ini(self):
        """Test INI generation."""
        ini_str = _generate_ini(self.test_config)
        # Simple check since INI is lossy
        self.assertIn("[database]", ini_str)
        self.assertIn("host = localhost", ini_str)
        self.assertIn("port = 5432", ini_str)

    def test_generate_yaml_file(self):
        """Test generating a YAML config file."""
        output_path = self.test_dir / "config.yaml"
        result_path = ConfigGenerator.generate(
            self.test_config_str, output_path, format="yaml"
        )
        self.assertTrue(result_path.exists())
        self.assertEqual(result_path.suffix, ".yaml")
        
        # Verify the content
        with open(result_path, 'r') as f:
            content = yaml.safe_load(f)
        self.assertEqual(content["database"]["name"], "testdb")

    def test_generate_toml_file(self):
        """Test generating a TOML config file."""
        output_path = self.test_dir / "config.toml"
        result_path = ConfigGenerator.generate(
            self.test_config_str, output_path, format="toml"
        )
        self.assertTrue(result_path.exists())
        
        # Verify the content
        with open(result_path, 'rb') as f:
            content = toml.load(f)
        self.assertEqual(content["database"]["port"], 5432)

    def test_generate_ini_file(self):
        """Test generating an INI config file."""
        output_path = self.test_dir / "config.ini"
        result_path = ConfigGenerator.generate(
            self.test_config_str, output_path, format="ini"
        )
        self.assertTrue(result_path.exists())
        
        # Simple check since INI is lossy
        with open(result_path, 'r') as f:
            content = f.read()
        self.assertIn("[database]", content)
        self.assertIn("port = 5432", content)

    def test_unsupported_format(self):
        """Test that an unsupported format raises an error."""
        with self.assertRaises(ValueError):
            ConfigGenerator.generate(
                self.test_config_str, 
                self.test_dir / "config.xyz", 
                format="xyz"
            )


if __name__ == "__main__":
    unittest.main()
