"""JAR / metadata parser tests against fixture packs."""

from pathlib import Path

import pytest

from app.models.mod import ModEnvironment, ModLoader
from app.parser.jar_parser import parse_jar
from fixtures.build_fixtures import build

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "modpacks"


@pytest.fixture(scope="session", autouse=True)
def _fixtures():
    build()


def test_parse_fabric_jar():
    mod = parse_jar(FIXTURES / "mini_fabric" / "mods" / "examplemod-1.0.0.jar")
    assert mod.parse_ok
    assert mod.mod_id == "examplemod"
    assert mod.loader == ModLoader.FABRIC
    assert mod.version == "1.0.0"
    assert any(d.mod_id == "librarymod" for d in mod.dependencies)


def test_parse_client_only():
    mod = parse_jar(FIXTURES / "mini_fabric" / "mods" / "sodium-extra-0.1.jar")
    assert mod.parse_ok
    assert mod.environment == ModEnvironment.CLIENT


def test_parse_forge_toml():
    mod = parse_jar(FIXTURES / "mini_forge" / "mods" / "curios-5.0.jar")
    assert mod.parse_ok
    assert mod.mod_id == "curios"
    assert mod.loader == ModLoader.FORGE


def test_parse_neoforge():
    mod = parse_jar(FIXTURES / "mini_neoforge" / "mods" / "neolib-1.0.jar")
    assert mod.parse_ok
    assert mod.mod_id == "neolib"
    assert mod.loader == ModLoader.NEOFORGE


def test_corrupt_jar_does_not_raise():
    mod = parse_jar(FIXTURES / "mini_corrupt" / "mods" / "broken.jar")
    assert not mod.parse_ok
    assert mod.parse_error
    assert "Corrupt" in mod.parse_error or "bad zip" in mod.parse_error.lower() or "zip" in mod.parse_error.lower()
