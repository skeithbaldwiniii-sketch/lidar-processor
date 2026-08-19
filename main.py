from pathlib import Path
from datetime import datetime
import time

from app.processor import process_folder


def show_progress(update):
    """Display processing progress in the terminal."""

    event = update["event"]

    if event == "processing":

        current = update["current"]
        total = update["total"]
        filename = update["file"].name

        print(
            f"[{current}/{total}] "
            f"Processing {filename}..."
        )

    elif event == "completed":

        result = update["result"]

        if result.status == "success":
            print("    ✓ Converted")

        elif result.status == "skipped":
            print("    → Skipped")
            print(f"      {result.message}")

        else:
            print("    ✗ FAILED")
            print(f"      {result.message}")

        print()

    elif event == "finished":

        print("Processing engine finished.")


def main():

    print("LiDAR Processor")
    print("================")
    print()

    start_time = time.perf_counter()
    start_datetime = datetime.now()

    project_root = Path(__file__).resolve().parent

    input_folder = project_root / "test_data"
    output_folder = project_root / "output"

    try:

        print(f"Input:  {input_folder}")
        print(f"Output: {output_folder}")
        print()

        summary = process_folder(
            input_folder,
            output_folder,
            progress_callback=show_progress,
        )

        elapsed_time = time.perf_counter() - start_time
        finish_datetime = datetime.now()

        print("================")
        print("Processing Complete")
        print("================")
        print()

        print(f"Started:   {start_datetime}")
        print(f"Finished:  {finish_datetime}")
        print(f"Duration:  {elapsed_time:.2f} seconds")
        print()

        print(f"Total:     {summary['total']}")
        print(f"Converted: {summary['successful']}")
        print(f"Skipped:   {summary['skipped']}")
        print(f"Failed:    {summary['failed']}")
        print()

        if summary["skipped_files"]:

            print("Skipped Files")
            print("-------------")

            for result in summary["skipped_files"]:
                print(result.input_file.name)
                print(f"  {result.message}")

            print()

        if summary["failed_files"]:

            print("Failed Files")
            print("------------")

            for result in summary["failed_files"]:
                print(result.input_file.name)
                print(f"  {result.message}")

            print()

        print(f"Output: {summary['output_folder']}")

    except Exception as error:

        print()
        print("================")
        print("PROCESSING ERROR")
        print("================")
        print(error)


if __name__ == "__main__":
    main()