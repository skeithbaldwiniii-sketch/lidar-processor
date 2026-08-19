import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
from datetime import datetime
from pathlib import Path

from app.processor import process_folder


class LiDARProcessorGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("LiDAR Processor")
        self.root.geometry("800x650")
        self.root.minsize(750, 600)

        self.processing = False
        self.start_time = None

        self.cancel_event = None

        self.last_summary = None
        self.last_option = None
        self.start_datetime = None
        self.finish_datetime = None

        self.build_interface()

    def build_interface(self):

        # =========================================================
        # TITLE
        # =========================================================

        title = tk.Label(
            self.root,
            text="LiDAR Processor",
            font=("Segoe UI", 22, "bold"),
        )

        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="LAZ → LAS Batch Processing",
            font=("Segoe UI", 10),
        )

        subtitle.pack(pady=(0, 20))

        # =========================================================
        # MAIN FRAME
        # =========================================================

        main_frame = tk.Frame(self.root)

        main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
        )

        # =========================================================
        # INPUT
        # =========================================================

        tk.Label(
            main_frame,
            text="Input LAZ Folder",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        input_frame = tk.Frame(main_frame)

        input_frame.pack(
            fill="x",
            pady=(5, 15),
        )

        self.input_entry = tk.Entry(
            input_frame,
            font=("Segoe UI", 10),
        )

        self.input_entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        tk.Button(
            input_frame,
            text="Browse",
            width=10,
            command=self.select_input_folder,
        ).pack(
            side="left",
            padx=(10, 0),
        )

        # =========================================================
        # OUTPUT
        # =========================================================

        tk.Label(
            main_frame,
            text="Output LAS Folder",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        output_frame = tk.Frame(main_frame)

        output_frame.pack(
            fill="x",
            pady=(5, 20),
        )

        self.output_entry = tk.Entry(
            output_frame,
            font=("Segoe UI", 10),
        )

        self.output_entry.pack(
            side="left",
            fill="x",
            expand=True,
        )

        tk.Button(
            output_frame,
            text="Browse",
            width=10,
            command=self.select_output_folder,
        ).pack(
            side="left",
            padx=(10, 0),
        )

        # =========================================================
        # OPTIONS
        # =========================================================

        tk.Label(
            main_frame,
            text="Options",
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(fill="x")

        self.recursive_var = tk.BooleanVar(value=True)
        self.preserve_var = tk.BooleanVar(value=True)
        self.skip_var = tk.BooleanVar(value=True)

        tk.Checkbutton(
            main_frame,
            text="Search subfolders",
            variable=self.recursive_var,
            anchor="w",
        ).pack(fill="x")

        tk.Checkbutton(
            main_frame,
            text="Preserve folder structure",
            variable=self.preserve_var,
            anchor="w",
        ).pack(fill="x")

        tk.Checkbutton(
            main_frame,
            text="Skip existing LAS files",
            variable=self.skip_var,
            anchor="w",
        ).pack(fill="x")

        # =========================================================
        # PROCESS BUTTON
        # =========================================================

        button_frame = tk.Frame(main_frame)

        button_frame.pack(
            pady=20,
        )

        self.process_button = tk.Button(
            button_frame,
            text="PROCESS",
            font=("Segoe UI", 11, "bold"),
            height=2,
            command=self.start_processing,
        )

        self.process_button.pack(
            side="left",
            ipadx=30,
        )

        self.cancel_button = tk.Button(
            button_frame,
            text="CANCEL",
            font=("Segoe UI", 11, "bold"),
            height=2,
            state="disabled",
            command=self.cancel_processing,
        )

        self.cancel_button.pack(
            side="left",
            padx=(10, 0),
            ipadx=20,
        )

        self.save_report_button = tk.Button(
            main_frame,
            text="SAVE REPORT",
            font=("Segoe UI", 10, "bold"),
            command=self.save_report,
        )

        self.save_report_button.pack(
            pady=(0, 10),
            ipadx=20,
        )

        # =========================================================
        # PROGRESS
        # =========================================================

        progress_frame = tk.LabelFrame(
            main_frame,
            text="Processing",
            padx=10,
            pady=10,
        )

        progress_frame.pack(
            fill="x",
            pady=(0, 10),
        )

        self.progress = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
        )

        self.progress.pack(
            fill="x",
            pady=(0, 10),
        )

        self.current_file_label = tk.Label(
            progress_frame,
            text="Ready",
            anchor="w",
        )

        self.current_file_label.pack(
            fill="x",
        )

        self.stats_label = tk.Label(
            progress_frame,
            text="Files: 0    Converted: 0    Skipped: 0    Failed: 0",
            anchor="w",
        )

        self.stats_label.pack(
            fill="x",
            pady=(5, 0),
        )

        # =========================================================
        # LOG
        # =========================================================

        log_frame = tk.LabelFrame(
            main_frame,
            text="Log",
            padx=10,
            pady=10,
        )

        log_frame.pack(
            fill="both",
            expand=True,
        )

        self.log = tk.Text(
            log_frame,
            height=8,
            font=("Consolas", 9),
            state="disabled",
        )

        self.log.pack(
            side="left",
            fill="both",
            expand=True,
        )

        scrollbar = tk.Scrollbar(
            log_frame,
            command=self.log.yview,
        )

        scrollbar.pack(
            side="right",
            fill="y",
        )

        self.log.configure(
            yscrollcommand=scrollbar.set
        )

    # =============================================================
    # FOLDER SELECTION
    # =============================================================

    def select_input_folder(self):

        folder = filedialog.askdirectory(
            title="Select LAZ Input Folder"
        )

        if folder:

            self.input_entry.delete(
                0,
                tk.END,
            )

            self.input_entry.insert(
                0,
                folder,
            )

    def select_output_folder(self):

        folder = filedialog.askdirectory(
            title="Select LAS Output Folder"
        )

        if folder:

            self.output_entry.delete(
                0,
                tk.END,
            )

            self.output_entry.insert(
                0,
                folder,
            )

    # =============================================================
    # LOGGING
    # =============================================================

    def add_log(self, message):

        self.log.configure(
            state="normal"
        )

        self.log.insert(
            tk.END,
            message + "\n",
        )

        self.log.see(
            tk.END
        )

        self.log.configure(
            state="disabled"
        )

    def save_report(self):
        """Save the most recent processing job as a text report."""

        if self.last_summary is None:
            messagebox.showwarning(
                "No Report Available",
                "Run a processing job before saving a report.",
            )
            return

        report_path = filedialog.asksaveasfilename(
            title="Save Processing Report",
            defaultextension=".txt",
            filetypes=[
                ("Text files", "*.txt"),
                ("All files", "*.*"),
            ],
            initialfile="lidar_processing_report.txt",
        )

        if not report_path:
            return

        summary = self.last_summary

        lines = []

        # ---------------------------------------------------------
        # HEADER
        # ---------------------------------------------------------

        lines.append("LiDAR PROCESSING REPORT")
        lines.append("=======================")
        lines.append("")

        # ---------------------------------------------------------
        # PROCESSING INFORMATION
        # ---------------------------------------------------------

        lines.append("PROCESSING INFORMATION")
        lines.append("----------------------")

        if self.start_datetime:
            lines.append(
                f"Started:   "
                f"{self.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        if self.finish_datetime:
            lines.append(
                f"Finished:  "
                f"{self.finish_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
            )

        if self.start_time:
            elapsed = time.perf_counter() - self.start_time
            lines.append(f"Duration:  {elapsed:.2f} seconds")

        lines.append("")

        # ---------------------------------------------------------
        # INPUT / OUTPUT
        # ---------------------------------------------------------

        lines.append("INPUT / OUTPUT")
        lines.append("--------------")

        lines.append(
            f"Input folder:\n{summary['input_folder']}"
        )

        lines.append("")

        lines.append(
            f"Output folder:\n{summary['output_folder']}"
        )

        lines.append("")

        # ---------------------------------------------------------
        # OPTIONS
        # ---------------------------------------------------------

        lines.append("OPTIONS")
        lines.append("-------")

        if self.last_options:

            lines.append(
                "Search subfolders:          "
                + (
                    "Yes"
                    if self.last_options["recursive"]
                    else "No"
                )
            )

            lines.append(
                "Preserve folder structure:  "
                + (
                    "Yes"
                    if self.last_options["preserve_structure"]
                    else "No"
                )
            )

            lines.append(
                "Skip existing LAS:          "
                + (
                    "Yes"
                    if self.last_options["skip_existing"]
                    else "No"
                )
            )

        lines.append("")

        # ---------------------------------------------------------
        # FILE RESULTS
        # ---------------------------------------------------------

        lines.append("FILES")
        lines.append("-----")

        results = summary.get("results", [])

        for number, result in enumerate(results, start=1):

            if result.status == "success":
                status = "CONVERTED"

            elif result.status == "skipped":
                status = "SKIPPED"

            else:
                status = "FAILED"

            lines.append(
                f"[{number}/{summary['total']}] {status}"
            )

            lines.append(
                f"Input:\n  {result.input_file}"
            )

            if result.output_file:
                lines.append(
                    f"Output:\n  {result.output_file}"
                )

            lines.append(
                f"Message:\n  {result.message}"
            )

            lines.append("")

        # ---------------------------------------------------------
        # SUMMARY
        # ---------------------------------------------------------

        lines.append("SUMMARY")
        lines.append("-------")

        lines.append(
            f"Total files:     {summary['total']}"
        )

        lines.append(
            f"Converted:       {summary['successful']}"
        )

        lines.append(
            f"Skipped:         {summary['skipped']}"
        )

        lines.append(
            f"Failed:          {summary['failed']}"
        )

        lines.append(
            f"Cancelled:       "
            f"{'Yes' if summary['cancelled'] else 'No'}"
        )

        lines.append("")

        # ---------------------------------------------------------
        # FINAL RESULT
        # ---------------------------------------------------------

        lines.append("RESULT")
        lines.append("------")

        if summary["cancelled"]:

            lines.append(
                "PROCESSING CANCELLED BY USER"
            )

        elif summary["failed"] > 0:

            lines.append(
                "PROCESSING COMPLETED WITH ERRORS"
            )

        else:

            lines.append(
                "PROCESSING COMPLETED SUCCESSFULLY"
            )

        lines.append("")

        report_text = "\n".join(lines)

        try:

            with open(
                report_path,
                "w",
                encoding="utf-8",
            ) as file:

                file.write(report_text)

            messagebox.showinfo(
                "Report Saved",
                f"Processing report saved to:\n\n{report_path}",
            )

        except OSError as error:

            messagebox.showerror(
                "Save Error",
                f"Could not save the report:\n\n{error}",
            )
    # =============================================================
    # START PROCESSING
    # =============================================================

    def start_processing(self):

        if self.processing:
            return

        input_folder = self.input_entry.get().strip()
        output_folder = self.output_entry.get().strip()

        if not input_folder:

            messagebox.showwarning(
                "Missing Input",
                "Please select an input LAZ folder.",
            )

            return

        if not output_folder:

            messagebox.showwarning(
                "Missing Output",
                "Please select an output LAS folder.",
            )

            return

        input_path = Path(input_folder)
        output_path = Path(output_folder)

        recursive = self.recursive_var.get()
        preserve_structure = self.preserve_var.get()
        skip_existing = self.skip_var.get()

        if not input_path.exists():

            messagebox.showerror(
                "Invalid Input",
                "The selected input folder does not exist.",
            )

            return

        self.processing = True
        self.start_time = time.perf_counter()

        self.start_datetime = datetime.now()

        self.last_options = {
            "recursive": recursive,
            "preserve_structure": preserve_structure,
            "skip_existing": skip_existing,
        }

        self.cancel_event = threading.Event()

        self.process_button.config(
            state="disabled",
            text="PROCESSING...",
        )

        self.cancel_button.config(
            state="normal",
        )

        self.progress["value"] = 0

        self.current_file_label.config(
            text="Starting..."
        )

        self.stats_label.config(
            text="Files: 0    Converted: 0    Skipped: 0    Failed: 0"
        )

        self.clear_log()

        self.add_log(
            "Starting LiDAR processing..."
        )

        self.add_log(
            f"Input: {input_path}"
        )

        self.add_log(
            f"Output: {output_path}"
        )

        # Run processing in background.
        thread = threading.Thread(
            target=self.run_processing,
            args=(
                input_path,
                output_path,
                recursive,
                preserve_structure,
                skip_existing,
                self.cancel_event,
            ),
            daemon=True,
        )

        thread.start()

    def cancel_processing(self):
        """Request that processing stop after the current file."""

        if not self.processing:
            return

        if self.cancel_event is not None:
            self.cancel_event.set()

        self.cancel_button.config(
            state="disabled",
        )

        self.current_file_label.config(
            text="Cancelling after current file..."
        )

        self.add_log(
            "Cancellation requested. "
            "Current file will finish first."
        )

    # =============================================================
    # BACKGROUND PROCESSING
    # =============================================================

    def run_processing(
        self,
        input_folder,
        output_folder,
        recursive,
        preserve_structure,
        skip_existing,
        cancel_event,
    ):

        try:

            summary = process_folder(
                input_folder,
                output_folder,
                recursive=recursive,
                preserve_structure=preserve_structure,
                skip_existing=skip_existing,
                progress_callback=self.progress_callback,
                cancel_event=cancel_event,
            )

            self.root.after(
                0,
                self.processing_finished,
                summary,
            )

        except Exception as error:

            self.root.after(
                0,
                self.processing_error,
                str(error),
            )

    # =============================================================
    # PROGRESS CALLBACK
    # =============================================================

    def progress_callback(self, update):

        self.root.after(
            0,
            self.update_interface,
            update,
        )

    # =============================================================
    # UPDATE GUI
    # =============================================================

    def update_interface(self, update):

        event = update["event"]

        if event == "started":

            total = update["total"]

            self.progress["maximum"] = max(total, 1)
            self.progress["value"] = 0

            self.current_file_label.config(
                text=f"Found {total} LAZ file(s)."
            )

            self.stats_label.config(
                text="Files: 0    Converted: 0    Skipped: 0    Failed: 0"
            )

            self.add_log(
                f"Found {total} LAZ file(s)."
            )

            return

        if event == "processing":

            current = update["current"]
            total = update["total"]

            self.progress["maximum"] = total
            self.progress["value"] = current - 1

            filename = update["file"].name

            self.current_file_label.config(
                text=f"Processing: {filename}"
            )

        elif event == "completed":

            current = update["current"]
            total = update["total"]

            result = update["result"]

            self.progress["maximum"] = total
            self.progress["value"] = current

            self.stats_label.config(
                text=(
                    f"Files: {current}/{total}    "
                    f"Converted: {update['successful']}    "
                    f"Skipped: {update['skipped']}    "
                    f"Failed: {update['failed']}"
                )
            )

            if result.status == "success":

                self.add_log(
                    f"✓ {result.input_file.name} converted"
                )

            elif result.status == "skipped":

                self.add_log(
                    f"→ {result.input_file.name} skipped"
                )

            else:

                self.add_log(
                    f"✗ {result.input_file.name} FAILED"
                )

                self.add_log(
                    f"    {result.message}"
                )

    # =============================================================
    # PROCESSING COMPLETE
    # =============================================================

    def processing_finished(self, summary):

        self.last_summary = summary
        self.finish_datetime = datetime.now()

        elapsed = (
            time.perf_counter()
            - self.start_time
        )

        self.processing = False

        self.process_button.config(
            state="normal",
            text="PROCESS",
        )

        self.cancel_button.config(
            state='disabled',
        )


        self.current_file_label.config(
            text="Processing complete."
        )

        self.progress["value"] = summary["total"]

        if summary["cancelled"]:
            processed = (
                summary["successful"]
                + summary["skipped"]
                + summary["failed"]
            )

            self.progress["value"] = processed

            self.current_file_label.config(
                text="Processing cancelled."
            )

        else:
            self.progress["value"] = summary["total"]

            self.current_file_label.config(
                text="Processing complete."
            )

        if summary["cancelled"]:
            self.add_log(
                "Processing was cancelled by the user."
            )

        self.add_log("")
        self.add_log("==============================")
        if summary["cancelled"]:
            self.add_log("Processing Cancelled")
        else:
            self.add_log("Processing Complete")
        self.add_log("==============================")

        self.add_log(
            f"Total: {summary['total']}"
        )

        self.add_log(
            f"Converted: {summary['successful']}"
        )

        self.add_log(
            f"Skipped: {summary['skipped']}"
        )

        self.add_log(
            f"Failed: {summary['failed']}"
        )

        self.add_log(
            f"Elapsed time: {elapsed:.2f} seconds"
        )

        messagebox.showinfo(
            "Processing Cancelled"
            if summary["cancelled"]
            else "Processing Complete",
            (
                (
                    "Processing was cancelled.\n\n"
                    if summary["cancelled"]
                    else
                    "Processing complete.\n\n"
                )
                + f"Total: {summary['total']}\n"
                + f"Converted: {summary['successful']}\n"
                + f"Skipped: {summary['skipped']}\n"
                + f"Failed: {summary['failed']}\n\n"
                + f"Time: {elapsed:.2f} seconds"
            ),
        )

    # =============================================================
    # PROCESSING ERROR
    # =============================================================

    def processing_error(self, error):

        self.processing = False

        self.process_button.config(
            state="normal",
            text="PROCESS",
        )

        self.current_file_label.config(
            text="Processing failed."
        )

        self.add_log("")
        self.add_log("PROCESSING ERROR")
        self.add_log(error)

        messagebox.showerror(
            "Processing Error",
            error,
        )

    # =============================================================
    # CLEAR LOG
    # =============================================================

    def clear_log(self):

        self.log.configure(
            state="normal"
        )

        self.log.delete(
            "1.0",
            tk.END,
        )

        self.log.configure(
            state="disabled"
        )


def main():

    root = tk.Tk()

    app = LiDARProcessorGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()