"""Build tiny fixture JAR files for parser/analyzer tests.

Run: python backend/fixtures/build_fixtures.py
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "modpacks"


def write_jar(path: Path, files: dict[str, str | bytes]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            data = content.encode("utf-8") if isinstance(content, str) else content
            zf.writestr(name, data)


def build() -> None:
    # --- mini_fabric: fabric mod with required + optional + conflict ---
    fabric_pack = ROOT / "mini_fabric" / "mods"
    write_jar(
        fabric_pack / "examplemod-1.0.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "examplemod",
                    "version": "1.0.0",
                    "name": "Example Mod",
                    "description": "A tiny Fabric fixture mod",
                    "authors": ["Fixture Author"],
                    "environment": "*",
                    "depends": {
                        "fabricloader": ">=0.14.0",
                        "minecraft": "1.20.1",
                        "fabric-api": "*",
                        "librarymod": ">=1.0.0",
                    },
                    "recommends": {"optionalmod": "*"},
                    "breaks": {"badmod": "*"},
                },
                indent=2,
            )
        },
    )
    write_jar(
        fabric_pack / "librarymod-1.2.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "librarymod",
                    "version": "1.2.0",
                    "name": "Library Mod",
                    "environment": "*",
                    "depends": {"minecraft": "1.20.1"},
                },
                indent=2,
            )
        },
    )
    write_jar(
        fabric_pack / "sodium-extra-0.1.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "sodiumextra",
                    "version": "0.1.0",
                    "name": "Sodium Extra",
                    "environment": "client",
                    "depends": {"minecraft": "1.20.1"},
                },
                indent=2,
            )
        },
    )

    # --- mini_forge: Forge mods.toml ---
    forge_pack = ROOT / "mini_forge" / "mods"
    write_jar(
        forge_pack / "curios-5.0.jar",
        {
            "META-INF/mods.toml": """
modLoader="javafml"
loaderVersion="[47,)"
license="MIT"

[[mods]]
modId="curios"
version="5.0.0"
displayName="Curios API"
description='''Curios fixture'''

[[dependencies.curios]]
modId="forge"
mandatory=true
versionRange="[47,)"
ordering="NONE"
side="BOTH"

[[dependencies.curios]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1,1.21)"
ordering="NONE"
side="BOTH"
""".strip()
        },
    )
    write_jar(
        forge_pack / "relics-1.0.jar",
        {
            "META-INF/mods.toml": """
modLoader="javafml"
loaderVersion="[47,)"
license="MIT"

[[mods]]
modId="relics"
version="1.0.0"
displayName="Relics"
description='''Needs Curios'''

[[dependencies.relics]]
modId="curios"
mandatory=true
versionRange="[5.0,)"
ordering="NONE"
side="BOTH"

[[dependencies.relics]]
modId="minecraft"
mandatory=true
versionRange="[1.20.1,1.21)"
ordering="NONE"
side="BOTH"
""".strip()
        },
    )

    # --- mini_neoforge ---
    neo_pack = ROOT / "mini_neoforge" / "mods"
    write_jar(
        neo_pack / "neolib-1.0.jar",
        {
            "META-INF/neoforge.mods.toml": """
modLoader="javafml"
loaderVersion="[1,)"
license="MIT"

[[mods]]
modId="neolib"
version="1.0.0"
displayName="Neo Lib"

[[dependencies.neolib]]
modId="neoforge"
type="required"
versionRange="[20,)"
ordering="NONE"
side="BOTH"

[[dependencies.neolib]]
modId="minecraft"
type="required"
versionRange="[1.20.1,1.21)"
ordering="NONE"
side="BOTH"
""".strip()
        },
    )

    # --- mini_missing_dep: requires absent mod ---
    missing = ROOT / "mini_missing_dep" / "mods"
    write_jar(
        missing / "needs-curios-1.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "needscurios",
                    "version": "1.0.0",
                    "name": "Needs Curios",
                    "environment": "*",
                    "depends": {"curios": ">=5.0.0", "minecraft": "1.20.1"},
                },
                indent=2,
            )
        },
    )

    # --- mini_duplicates: two JEI versions + identical copy ---
    dups = ROOT / "mini_duplicates" / "mods"
    jei_meta_a = json.dumps(
        {
            "schemaVersion": 1,
            "id": "jei",
            "version": "10.0.0",
            "name": "Just Enough Items",
            "environment": "*",
            "depends": {"minecraft": "1.20.1"},
        },
        indent=2,
    )
    jei_meta_b = json.dumps(
        {
            "schemaVersion": 1,
            "id": "jei",
            "version": "11.0.0",
            "name": "Just Enough Items",
            "environment": "*",
            "depends": {"minecraft": "1.20.1"},
        },
        indent=2,
    )
    write_jar(dups / "jei-10.0.0.jar", {"fabric.mod.json": jei_meta_a})
    write_jar(dups / "jei-11.0.0.jar", {"fabric.mod.json": jei_meta_b})
    # Identical byte copy of jei-11
    write_jar(dups / "jei-11.0.0-copy.jar", {"fabric.mod.json": jei_meta_b})

    # --- mini_corrupt: not a zip ---
    corrupt = ROOT / "mini_corrupt" / "mods"
    corrupt.mkdir(parents=True, exist_ok=True)
    (corrupt / "broken.jar").write_bytes(b"this is not a jar file at all!!!")

    # --- mini_circular: A→B→A ---
    circular = ROOT / "mini_circular" / "mods"
    write_jar(
        circular / "moda-1.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "moda",
                    "version": "1.0.0",
                    "name": "Mod A",
                    "environment": "*",
                    "depends": {"modb": "*"},
                },
                indent=2,
            )
        },
    )
    write_jar(
        circular / "modb-1.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "modb",
                    "version": "1.0.0",
                    "name": "Mod B",
                    "environment": "*",
                    "depends": {"moda": "*"},
                },
                indent=2,
            )
        },
    )

    # --- mini_version_conflict: needs librarymod >=2.0 but 1.0 installed ---
    ver = ROOT / "mini_version_conflict" / "mods"
    write_jar(
        ver / "consumer-1.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "consumer",
                    "version": "1.0.0",
                    "name": "Consumer",
                    "environment": "*",
                    "depends": {"librarymod": ">=2.0.0"},
                },
                indent=2,
            )
        },
    )
    write_jar(
        ver / "librarymod-1.0.0.jar",
        {
            "fabric.mod.json": json.dumps(
                {
                    "schemaVersion": 1,
                    "id": "librarymod",
                    "version": "1.0.0",
                    "name": "Library Mod",
                    "environment": "*",
                    "depends": {},
                },
                indent=2,
            )
        },
    )

    # empty config folders for realism
    for pack in ROOT.iterdir():
        if pack.is_dir():
            (pack / "config").mkdir(exist_ok=True)

    print(f"Fixtures written under {ROOT}")


if __name__ == "__main__":
    build()
