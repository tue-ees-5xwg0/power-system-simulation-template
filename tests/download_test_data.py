import shutil
import stat
import tempfile
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath, PureWindowsPath

ASSET_NAME = "assignment_test_data.zip"
DOWNLOAD_URL = "https://github.com/tue-ees-5xwg0/assignment-test-data/releases/latest/download/assignment_test_data.zip"
DATA_DIR = Path(__file__).resolve().parent / "data"


def check_cache() -> bool:
    return DATA_DIR.is_dir() and any(DATA_DIR.iterdir())


def extract_archive(archive_path: Path, destination: Path) -> int:
    destination.mkdir(parents=True, exist_ok=True)
    destination_root = destination.resolve()
    extracted_files = 0

    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            path = PurePosixPath(member.filename)
            windows_path = PureWindowsPath(member.filename)
            if (
                not member.filename
                or "\x00" in member.filename
                or "\\" in member.filename
                or path.is_absolute()
                or windows_path.is_absolute()
                or windows_path.drive
                or ".." in path.parts
            ):
                raise ValueError(f"Unsafe path in ZIP archive: {member.filename!r}")

            if stat.S_ISLNK(member.external_attr >> 16):
                raise ValueError(f"Symbolic link in ZIP archive: {member.filename!r}")

            if not path.parts:
                continue

            target = destination.joinpath(*path.parts).resolve()
            if not target.is_relative_to(destination_root):
                raise ValueError(f"ZIP member escapes destination: {member.filename!r}")

            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
                continue

            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, target.open("wb") as output:
                shutil.copyfileobj(source, output)
            extracted_files += 1

    return extracted_files


def download_test_data(force: bool = False) -> Path:
    if not force and check_cache():
        print(f"Using cached test data in {DATA_DIR}.")
        return DATA_DIR

    print(f"Downloading {ASSET_NAME} from the latest release...")
    with tempfile.TemporaryDirectory() as temporary_directory:
        archive_path = Path(temporary_directory) / ASSET_NAME
        with urllib.request.urlopen(DOWNLOAD_URL, timeout=60) as response, archive_path.open("wb") as archive:
            shutil.copyfileobj(response, archive)

        print(f"Extracting files into {DATA_DIR}...")
        file_count = extract_archive(archive_path, DATA_DIR)

    print(f"Extracted {file_count} files.")
    return DATA_DIR


def main() -> None:
    download_test_data(force=True)


if __name__ == "__main__":
    main()
