"""Find a team's agents and copy them somewhere safe before anything runs."""
from __future__ import annotations

import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path

from .config import ROOT

AGENT_FILES = {
    "road_trip": "roadtrip_agent.py",
    "chess": "chess_agent.py",
    "battleship": "battleship_agent.py",
    "catan": "catan_agent.py",
}
GAME_OF_FILE = {filename: game for game, filename in AGENT_FILES.items()}
DEMO_TEAMS = {"demo": "team_demo_A", "demo_a": "team_demo_A", "demo_b": "team_demo_B"}


class TeamError(Exception):
    """A team's folder cannot be used. The message says exactly why."""


@dataclass
class Team:
    name: str
    folder: Path  # the private copy that actually runs, never the original

    def agent(self, game: str) -> Path:
        return self.folder / AGENT_FILES[game]


def missing_files(folder, games=None) -> list:
    wanted = games or AGENT_FILES
    return [AGENT_FILES[game] for game in wanted if not (Path(folder) / AGENT_FILES[game]).is_file()]


def _unzip_team(path: Path) -> Path:
    """Colab's Files panel uploads files, not folders, so a team may arrive as a zip."""
    target = Path(tempfile.mkdtemp(prefix="unzipped_"))
    try:
        with zipfile.ZipFile(path) as bundle:
            bundle.extractall(target)
    except zipfile.BadZipFile as error:
        raise TeamError(f"{path.name} is not a valid zip file") from error
    folders = [target] + [p for p in sorted(target.rglob("*")) if p.is_dir() and "__MACOSX" not in p.parts]
    return min(folders, key=lambda folder: len(missing_files(folder)))


def _locate(spec: str) -> Path:
    """A short name like "Team_03.zip" works: the notebook runs inside the package
    folder, while uploaded files land one level above it."""
    path = Path(spec).expanduser()
    if path.is_absolute():
        return path
    for base in (Path.cwd(), ROOT.parent):
        for candidate in (base / path, base / f"{path}.zip"):
            if candidate.exists():
                return candidate
    return path


def _not_found(source: Path) -> TeamError:
    nearby = sorted({
        found.name
        for base in (Path.cwd(), ROOT.parent)
        for pattern in ("*.zip", "*.py")
        for found in base.glob(pattern)
        if found.name != "ai_agent_tournament.zip"
    })
    hint = f" Files I can see: {', '.join(nearby)}." if nearby else ""
    return TeamError(f"Team folder or zip not found: {source}.{hint}")


def _team_of_one_file(source: Path, games) -> Team:
    """For practice: one .py plays one game, whatever the file is called."""
    if not games or len(games) != 1:
        raise TeamError(f"{source.name} is a single file, so it can only practise one game. "
                        "A full match needs a folder or zip with all four agents.")
    copy_dir = Path(tempfile.mkdtemp(prefix=f"team_{source.stem}_"))
    shutil.copy2(source, copy_dir / AGENT_FILES[games[0]])
    return Team(source.stem, copy_dir)


def load_team(spec, games=None) -> Team:
    """spec is a folder or a .zip of one, "demo_a" / "demo_b" for the example teams,
    or, to practise one game, a single .py file.

    The .py files are copied first, so the originals are never modified and a
    mounted Google Drive can be disconnected before any agent runs.
    """
    spec = str(spec)
    source = ROOT / "examples" / DEMO_TEAMS[spec] if spec in DEMO_TEAMS else _locate(spec)
    name = spec if spec in DEMO_TEAMS else source.stem
    if source.is_file() and source.suffix == ".py":
        return _team_of_one_file(source, games)
    if source.is_file() and source.suffix == ".zip":
        source = _unzip_team(source)
    if not source.is_dir():
        raise _not_found(source)
    absent = missing_files(source, games)
    if absent:
        raise TeamError(f"Team {name} is incomplete. Missing: {', '.join(absent)}")
    copy_dir = Path(tempfile.mkdtemp(prefix=f"team_{name}_"))
    for game in games or AGENT_FILES:
        shutil.copy2(source / AGENT_FILES[game], copy_dir / AGENT_FILES[game])
    return Team(name, copy_dir)


def list_teams(parent) -> dict:
    """Every subfolder of parent, with the agent files it is missing (empty = ready)."""
    parent = Path(parent).expanduser()
    if not parent.is_dir():
        raise TeamError(f"Folder not found: {parent}")
    return {
        child.name: missing_files(child)
        for child in sorted(parent.iterdir())
        if child.is_dir() and not child.name.startswith((".", "_"))
    }
