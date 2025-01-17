import tomllib
import re
import sys
from typing import List, Dict, Any


def get_version_from_pyproject() -> str:
    """Read the version from pyproject.toml."""
    with open("pyproject.toml", "rb") as f:
        pyproject: Dict[str, Any] = tomllib.load(f)
    version: str = pyproject["project"]["version"]
    return version


def update_version_badge(md_files: List[str], version: str) -> None:
    """Update the version badge in multiple Markdown files."""
    badge_pattern: str = (
        r"\[!\[Version\]\(https://img.shields.io/badge/version-[\d\.\w]+-blue\)\]\(#\)"
    )
    new_badge: str = (
        f"[![Version](https://img.shields.io/badge/version-{version}-blue)](#)"
    )

    for md_file in md_files:
        try:
            with open(md_file, "r") as f:
                content: str = f.read()

            updated_content: str = re.sub(badge_pattern, new_badge, content)

            with open(md_file, "w") as f:
                f.write(updated_content)

            print(f"Updated version badge in {md_file}.")
        except FileNotFoundError:
            print(f"File not found: {md_file}")
        except Exception as e:
            print(f"Error updating {md_file}: {e}")


def check_changelog_version(changelog_file: str, version: str) -> bool:
    """Check if the version exists in the CHANGELOG.md file."""
    try:
        with open(changelog_file, "r") as f:
            content: str = f.read()

        dev_version_pattern: str = (
            rf"## \[{re.escape(version)}\] - \d{{4}}-\d{{2}}-\d{{2}}"
        )
        published_version: str = re.sub(r"\.dev\d+", "", version)
        published_version_pattern: str = (
            rf"## \[{re.escape(published_version)}\] - \d{{4}}-\d{{2}}-\d{{2}}"
        )

        if re.search(dev_version_pattern, content) or re.search(
            published_version_pattern, content
        ):
            print(
                f"Version {version} (or {published_version}) is listed in {changelog_file}. ✅"
            )
            return True
        else:
            print(
                f"Version {version} (or {published_version}) is NOT listed in {changelog_file}. ❌"
            )
            return False
    except FileNotFoundError:
        print(f"File not found: {changelog_file}")
        return False
    except Exception as e:
        print(f"Error reading {changelog_file}: {e}")
        return False


if __name__ == "__main__":
    # Files to update
    md_files = ["README.md", "docs/index.md"]
    changelog_file = "docs/CHANGELOG.md"

    version = get_version_from_pyproject()
    update_version_badge(md_files, version)
    changelog_status = check_changelog_version(changelog_file, version)
    if not changelog_status:
        print("Error: The version is not listed in the CHANGELOG.md file.")
        sys.exit(1)
    else:
        print("Version verification and badge update completed successfully!")
