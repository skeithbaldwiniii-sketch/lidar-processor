from pathlib import Path
import subprocess
import sys
from dataclasses import dataclass


@dataclass
class ConversionResult:
    input_file: Path
    output_file: Path | None
    status: str
    message: str


def find_laszip() -> Path:
    """Find the bundled laszip64 executable."""

    if getattr(sys, "frozen", False):
        # Running as a PyInstaller executable.
        base_path = Path(sys._MEIPASS)
    else:
        # Running from the Python source project.
        base_path = Path(__file__).resolve().parent.parent

    laszip_path = (
        base_path
        / "tools"
        / "laszip64.exe"
    )

    if not laszip_path.exists():
        raise FileNotFoundError(
            f"Could not find laszip64.exe at:\n{laszip_path}"
        )

    return laszip_path


def find_laz_files(
    input_folder: Path,
    recursive: bool = True,
) -> list[Path]:
    """Find LAZ files in the input folder."""

    if not input_folder.exists():
        raise FileNotFoundError(
            f"Input folder does not exist:\n{input_folder}"
        )

    if recursive:
        files = input_folder.rglob("*")
    else:
        files = input_folder.iterdir()

    return sorted(
        file
        for file in files
        if file.is_file() and file.suffix.lower() == ".laz"
    )


def convert_laz_to_las(
    laz_file: Path,
    output_file: Path,
    laszip_path: Path,
) -> ConversionResult:
    """Convert one LAZ file to LAS."""

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    command = [
        str(laszip_path),
        "-i",
        str(laz_file),
        "-o",
        str(output_file),
    ]

    try:

        creation_flags = 0

        if hasattr(subprocess, "CREATE_NO_WINDOW"):
            creation_flags = subprocess.CREATE_NO_WINDOW

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=creation_flags,
        )

    except OSError as error:
        return ConversionResult(
            input_file=laz_file,
            output_file=None,
            status="failed",
            message=f"Could not start laszip64: {error}",
        )

    if result.returncode != 0:
        error_message = result.stderr.strip()

        if not error_message:
            error_message = result.stdout.strip()

        return ConversionResult(
            input_file=laz_file,
            output_file=None,
            status="failed",
            message=(
                error_message
                or "Unknown conversion error."
            ),
        )

    if not output_file.exists():
        return ConversionResult(
            input_file=laz_file,
            output_file=None,
            status="failed",
            message=(
                "laszip64 completed, but no LAS file "
                "was created."
            ),
        )

    return ConversionResult(
        input_file=laz_file,
        output_file=output_file,
        status="success",
        message="Conversion completed successfully.",
    )


def process_folder(
    input_folder: Path,
    output_folder: Path,
    recursive: bool = True,
    preserve_structure: bool = True,
    skip_existing: bool = True,
    progress_callback=None,
    cancel_event=None,
) -> dict:
    """
    Process LAZ files from an input folder.

    Cancellation is checked between files. The currently running
    conversion is allowed to finish safely before processing stops.
    """

    input_folder = Path(input_folder)
    output_folder = Path(output_folder)

    laszip_path = find_laszip()

    laz_files = find_laz_files(
        input_folder,
        recursive=recursive,
    )

    total = len(laz_files)

    successful = 0
    skipped = 0
    failed = 0

    results = []
    skipped_files = []
    failed_files = []

    cancelled = False

    if progress_callback:
        progress_callback(
            {
                "event": "started",
                "total": total,
            }
        )

    for number, laz_file in enumerate(laz_files, start=1):

        # Check for cancellation before starting another file.
        if cancel_event is not None and cancel_event.is_set():
            cancelled = True
            break

        if progress_callback:
            progress_callback(
                {
                    "event": "processing",
                    "current": number,
                    "total": total,
                    "file": laz_file,
                    "successful": successful,
                    "skipped": skipped,
                    "failed": failed,
                }
            )

        # Determine output location.
        if preserve_structure:
            relative_path = laz_file.relative_to(input_folder)

            output_file = (
                output_folder
                / relative_path.parent
                / f"{laz_file.stem}.las"
            )
        else:
            output_file = (
                output_folder
                / f"{laz_file.stem}.las"
            )

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Handle existing files.
        if output_file.exists() and skip_existing:
            result = ConversionResult(
                input_file=laz_file,
                output_file=output_file,
                status="skipped",
                message="Output file already exists.",
            )

        else:
            result = convert_laz_to_las(
                laz_file,
                output_file,
                laszip_path,
            )

        # Track result.
        if result.status == "success":
            successful += 1

        elif result.status == "skipped":
            skipped += 1
            skipped_files.append(result)

        else:
            failed += 1
            failed_files.append(result)

        results.append(result)

        if progress_callback:
            progress_callback(
                {
                    "event": "completed",
                    "current": number,
                    "total": total,
                    "file": laz_file,
                    "result": result,
                    "successful": successful,
                    "skipped": skipped,
                    "failed": failed,
                }
            )

    # If cancellation was requested after the final file, report it
    # only if there were actually files left unprocessed.
    if (
        cancel_event is not None
        and cancel_event.is_set()
        and successful + skipped + failed < total
    ):
        cancelled = True

    summary = {
        "total": total,
        "successful": successful,
        "skipped": skipped,
        "failed": failed,
        "cancelled": cancelled,
        "skipped_files": skipped_files,
        "failed_files": failed_files,
        "results": results,
        "input_folder": input_folder,
        "output_folder": output_folder,
    }

    if progress_callback:
        progress_callback(
            {
                "event": "finished",
                "summary": summary,
            }
        )

    return summary