"""Parsers — turn JAR files into normalized Mod objects. Never execute JARs."""

from .jar_parser import parse_jar
from .version_parser import Version, parse_constraint, satisfies

__all__ = ["parse_jar", "Version", "parse_constraint", "satisfies"]
