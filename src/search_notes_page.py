"""
Search Notes Page - Search past work log entries and export results.

Allows users to:
  - Search notes by keyword across a date range (yesterday, last 7 days, custom)
  - View every matching entry with its timestamp, title, and AI summary
  - Export results as:
      • Markdown  — formal headed report suitable for a manager/boss review
      • CSV       — spreadsheet-friendly data for checks and analysis
      • Highlights — a plain-text digest of the most interesting / AI-summarised entries
"""
import csv
import datetime
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import theme
from data_repository import DataRepository

_MARKER_TITLES = ("DAY STARTED", "DAY ENDED", "HOURLY SUMMARY", "END OF DAY SUMMARY")


def _is_marker(title: str) -> bool:
    return any(m in title for m in _MARKER_TITLES)


class SearchNotesPage(tk.Frame):
    """Page for searching past work log notes and exporting results."""

    def __init__(self, parent, data_repository: DataRepository):
        """
        Initialise the Search Notes page.

        Args:
            parent: Parent tkinter widget.
            data_repository: Data repository instance.
        """
        super().__init__(parent, bg=theme.WINDOW_BG)
        self.data_repository = data_repository
        self._results: list = []
        self._create_widgets()

    # ── Widget construction ───────────────────────────────────────────────────

    def _create_widgets(self):
        # ── Header ────────────────────────────────────────────────────────────
        header_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        header_frame.pack(fill='x', padx=10, pady=(10, 4))

        tk.Label(
            header_frame, text="Search Notes",
            font=theme.FONT_H2, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(side='left')

        # ── Keyword row ───────────────────────────────────────────────────────
        kw_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        kw_frame.pack(fill='x', padx=10, pady=2)

        tk.Label(
            kw_frame, text="Keyword:",
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(side='left', padx=(0, 5))

        self.keyword_var = tk.StringVar()
        keyword_entry = tk.Entry(
            kw_frame, textvariable=self.keyword_var, width=30,
            bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief='flat',
        )
        keyword_entry.pack(side='left', padx=(0, 8))
        keyword_entry.bind('<Return>', lambda _e: self._run_search())

        # ── Date range row ────────────────────────────────────────────────────
        date_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        date_frame.pack(fill='x', padx=10, pady=2)

        tk.Label(
            date_frame, text="From:",
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(side='left', padx=(0, 4))

        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.date.today().strftime("%Y-%m-%d")

        self.from_var = tk.StringVar(value=yesterday)
        tk.Entry(
            date_frame, textvariable=self.from_var, width=12,
            bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief='flat',
        ).pack(side='left', padx=(0, 8))

        tk.Label(
            date_frame, text="To:",
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(side='left', padx=(0, 4))

        self.to_var = tk.StringVar(value=today_str)
        tk.Entry(
            date_frame, textvariable=self.to_var, width=12,
            bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief='flat',
        ).pack(side='left', padx=(0, 8))

        # Quick date range shortcuts
        theme.RoundedButton(
            date_frame, text="Yesterday", command=self._set_yesterday,
            bg=theme.SURFACE_BG, fg=theme.TEXT, width=10, cursor='hand2',
        ).pack(side='left', padx=2)
        theme.RoundedButton(
            date_frame, text="Last 7 Days", command=self._set_last_7,
            bg=theme.SURFACE_BG, fg=theme.TEXT, width=11, cursor='hand2',
        ).pack(side='left', padx=2)
        theme.RoundedButton(
            date_frame, text="Last 30 Days", command=self._set_last_30,
            bg=theme.SURFACE_BG, fg=theme.TEXT, width=12, cursor='hand2',
        ).pack(side='left', padx=2)
        theme.RoundedButton(
            date_frame, text="All Time", command=self._set_all_time,
            bg=theme.SURFACE_BG, fg=theme.TEXT, width=9, cursor='hand2',
        ).pack(side='left', padx=2)

        # ── Search button row ─────────────────────────────────────────────────
        search_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        search_frame.pack(fill='x', padx=10, pady=6)

        theme.RoundedButton(
            search_frame, text="Search", command=self._run_search,
            bg=theme.PRIMARY, fg=theme.TEXT,
            font=theme.FONT_BODY_BOLD, width=10, cursor='hand2',
        ).pack(side='left', padx=(0, 6))

        self.status_label = tk.Label(
            search_frame, text="Enter a keyword and press Search",
            font=theme.FONT_SMALL, bg=theme.WINDOW_BG, fg=theme.MUTED,
        )
        self.status_label.pack(side='left')

        # ── Results treeview ──────────────────────────────────────────────────
        list_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 4))

        columns = ('date', 'time', 'ticket', 'title', 'summary')
        self.result_tree = ttk.Treeview(
            list_frame, columns=columns, show='headings', height=12,
        )
        self.result_tree.heading('date', text='Date')
        self.result_tree.heading('time', text='Time')
        self.result_tree.heading('ticket', text='Ticket')
        self.result_tree.heading('title', text='Title / Notes')
        self.result_tree.heading('summary', text='AI Summary')

        self.result_tree.column('date', width=90, stretch=False)
        self.result_tree.column('time', width=60, stretch=False)
        self.result_tree.column('ticket', width=90, stretch=False)
        self.result_tree.column('title', width=250)
        self.result_tree.column('summary', width=350)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical',
                                  command=self.result_tree.yview)
        self.result_tree.configure(yscrollcommand=scrollbar.set)
        self.result_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Double-click shows full detail popup
        self.result_tree.bind('<Double-1>', self._show_detail)

        # ── Export buttons ────────────────────────────────────────────────────
        export_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        export_frame.pack(fill='x', padx=10, pady=(4, 10))

        tk.Label(
            export_frame, text="Export results as:",
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.MUTED,
        ).pack(side='left', padx=(0, 8))

        theme.RoundedButton(
            export_frame, text="📄 Markdown (Boss Review)",
            command=self._export_markdown,
            bg=theme.PRIMARY_D, fg=theme.TEXT,
            font=theme.FONT_BODY, width=22, cursor='hand2',
        ).pack(side='left', padx=3)

        theme.RoundedButton(
            export_frame, text="📊 CSV (Data Check)",
            command=self._export_csv,
            bg=theme.SURFACE_BG, fg=theme.TEXT,
            font=theme.FONT_BODY, width=18, cursor='hand2',
        ).pack(side='left', padx=3)

        theme.RoundedButton(
            export_frame, text="✨ Highlights",
            command=self._export_highlights,
            bg=theme.ACCENT, fg=theme.WINDOW_BG,
            font=theme.FONT_BODY, width=12, cursor='hand2',
        ).pack(side='left', padx=3)

    # ── Date shortcut helpers ─────────────────────────────────────────────────

    def _set_yesterday(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        self.from_var.set(yesterday.strftime("%Y-%m-%d"))
        self.to_var.set(yesterday.strftime("%Y-%m-%d"))

    def _set_last_7(self):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=6)
        self.from_var.set(start.strftime("%Y-%m-%d"))
        self.to_var.set(end.strftime("%Y-%m-%d"))

    def _set_last_30(self):
        end = datetime.date.today()
        start = end - datetime.timedelta(days=29)
        self.from_var.set(start.strftime("%Y-%m-%d"))
        self.to_var.set(end.strftime("%Y-%m-%d"))

    def _set_all_time(self):
        self.from_var.set("")
        self.to_var.set("")

    # ── Date parsing helper ───────────────────────────────────────────────────

    def _parse_date_range(self) -> tuple:
        """Return (start_date, end_date) or raise ValueError."""
        from_str = self.from_var.get().strip()
        to_str = self.to_var.get().strip()
        start_date: Optional[datetime.date] = None
        end_date: Optional[datetime.date] = None
        if from_str:
            start_date = datetime.datetime.strptime(from_str, "%Y-%m-%d").date()
        if to_str:
            end_date = datetime.datetime.strptime(to_str, "%Y-%m-%d").date()
        return start_date, end_date

    # ── Search ────────────────────────────────────────────────────────────────

    def _run_search(self):
        """Execute the keyword search and populate the results treeview."""
        keyword = self.keyword_var.get().strip()
        if not keyword:
            messagebox.showinfo(
                "Keyword Required",
                "Please enter a keyword to search for.\n\n"
                "For example: 'standup', 'bug fix', or a ticket number.",
            )
            return

        try:
            start_date, end_date = self._parse_date_range()
        except ValueError:
            messagebox.showerror(
                "Invalid Date",
                "Please enter dates in YYYY-MM-DD format, or leave them blank for no limit.",
            )
            return

        # Clear old results
        for item in self.result_tree.get_children():
            self.result_tree.delete(item)
        self._results = []

        raw = self.data_repository.search_tasks(keyword, start_date, end_date)
        self._results = [r for r in raw if not _is_marker(r.get('Title', ''))]

        for task in self._results:
            start_str = task.get('Start Time', '')
            date_disp, time_disp = '', ''
            if start_str:
                try:
                    dt = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    date_disp = dt.strftime("%Y-%m-%d")
                    time_disp = dt.strftime("%H:%M")
                except ValueError:
                    date_disp = start_str

            summary_short = task.get('AI Summary', '').replace('\n', ' ')[:120]
            if len(task.get('AI Summary', '')) > 120:
                summary_short += '…'

            self.result_tree.insert('', 'end', values=(
                date_disp,
                time_disp,
                task.get('Ticket', ''),
                task.get('Title', ''),
                summary_short,
            ))

        count = len(self._results)
        date_range_label = self._date_range_label(start_date, end_date)
        self.status_label.config(
            text=f"Found {count} result(s) for '{keyword}'{date_range_label}",
        )

    def _date_range_label(self, start_date, end_date) -> str:
        if start_date and end_date:
            if start_date == end_date:
                return f" on {start_date}"
            return f" between {start_date} and {end_date}"
        if start_date:
            return f" from {start_date}"
        if end_date:
            return f" up to {end_date}"
        return " (all time)"

    # ── Detail popup ──────────────────────────────────────────────────────────

    def _show_detail(self, _event):
        """Show full details for the double-clicked result."""
        selection = self.result_tree.selection()
        if not selection:
            return
        idx = self.result_tree.index(selection[0])
        if idx >= len(self._results):
            return
        task = self._results[idx]

        win = tk.Toplevel(self)
        win.title("Entry Detail")
        win.geometry("600x400")
        win.configure(bg=theme.WINDOW_BG)
        win.transient(self)

        tk.Label(
            win, text=f"{task.get('Start Time', '')}  —  {task.get('Ticket', '(no ticket)')}",
            font=theme.FONT_BODY_BOLD, bg=theme.WINDOW_BG, fg=theme.PRIMARY,
        ).pack(anchor='w', padx=15, pady=(12, 2))

        tk.Label(
            win, text=task.get('Title', ''),
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.TEXT,
            wraplength=560, justify='left',
        ).pack(anchor='w', padx=15, pady=(0, 8))

        tk.Label(
            win, text="AI Summary:",
            font=theme.FONT_BODY_BOLD, bg=theme.WINDOW_BG, fg=theme.MUTED,
        ).pack(anchor='w', padx=15)

        summary_box = tk.Text(
            win, height=10, wrap=tk.WORD,
            font=theme.FONT_BODY, bg=theme.INPUT_BG, fg=theme.TEXT,
            relief='flat', padx=6, pady=4, state='disabled',
        )
        summary_box.pack(fill='both', expand=True, padx=15, pady=(4, 12))
        summary_box.config(state='normal')
        summary_box.insert('1.0', task.get('AI Summary', '(no summary)'))
        summary_box.config(state='disabled')

        theme.RoundedButton(
            win, text="Close", command=win.destroy,
            bg=theme.SURFACE_BG, fg=theme.TEXT, width=8, cursor='hand2',
        ).pack(pady=(0, 10))

    # ── Export helpers ────────────────────────────────────────────────────────

    def _require_results(self) -> bool:
        if not self._results:
            messagebox.showinfo(
                "No Results",
                "Please run a search first to produce results to export.",
            )
            return False
        return True

    def _ask_save_path(self, title: str, default_ext: str, filetypes: list) -> Optional[str]:
        path = filedialog.asksaveasfilename(
            title=title,
            defaultextension=default_ext,
            filetypes=filetypes,
        )
        return path or None

    # ── Export: Markdown ──────────────────────────────────────────────────────

    def _export_markdown(self):
        """Export results as a formal Markdown report for boss/manager review."""
        if not self._require_results():
            return

        path = self._ask_save_path(
            "Save Markdown Report",
            ".md",
            [("Markdown files", "*.md"), ("All files", "*.*")],
        )
        if not path:
            return

        keyword = self.keyword_var.get().strip()
        from_str = self.from_var.get().strip() or "—"
        to_str = self.to_var.get().strip() or "—"
        generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            f"# Work Log Review — {keyword}",
            "",
            f"**Generated:** {generated_at}  ",
            f"**Search keyword:** `{keyword}`  ",
            f"**Date range:** {from_str} → {to_str}  ",
            f"**Total entries:** {len(self._results)}",
            "",
            "---",
            "",
        ]

        # Group entries by date
        by_date: dict = {}
        for task in self._results:
            start_str = task.get('Start Time', '')
            try:
                dt = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                day_key = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
            except ValueError:
                day_key = "Unknown Date"
                time_str = ""
            by_date.setdefault(day_key, []).append((time_str, task))

        for day in sorted(by_date.keys()):
            lines.append(f"## {day}")
            lines.append("")
            for time_str, task in sorted(by_date[day], key=lambda x: x[0]):
                ticket = task.get('Ticket', '') or '—'
                title = task.get('Title', '').replace('\n', ' ')
                summary = task.get('AI Summary', '').strip() or '*(no AI summary)*'
                lines.append(f"### {time_str} — {ticket}")
                lines.append("")
                lines.append(f"**Notes:** {title}")
                lines.append("")
                lines.append("**Summary of Thoughts:**")
                lines.append("")
                # Indent summary lines
                for para in summary.splitlines():
                    lines.append(f"> {para}" if para.strip() else ">")
                lines.append("")
                lines.append("---")
                lines.append("")

        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(lines))
            messagebox.showinfo("Exported", f"Markdown report saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    # ── Export: CSV ───────────────────────────────────────────────────────────

    def _export_csv(self):
        """Export results as a CSV file for data checking."""
        if not self._require_results():
            return

        path = self._ask_save_path(
            "Save CSV Export",
            ".csv",
            [("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return

        fieldnames = ["Date", "Time", "Ticket", "Title", "Duration (Min)",
                      "AI Summary", "Resolved"]

        try:
            with open(path, 'w', newline='', encoding='utf-8') as fh:
                writer = csv.DictWriter(fh, fieldnames=fieldnames)
                writer.writeheader()
                for task in self._results:
                    start_str = task.get('Start Time', '')
                    date_val, time_val = '', ''
                    try:
                        dt = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                        date_val = dt.strftime("%Y-%m-%d")
                        time_val = dt.strftime("%H:%M")
                    except ValueError:
                        date_val = start_str
                    writer.writerow({
                        "Date": date_val,
                        "Time": time_val,
                        "Ticket": task.get('Ticket', ''),
                        "Title": task.get('Title', ''),
                        "Duration (Min)": task.get('Duration (Min)', ''),
                        "AI Summary": task.get('AI Summary', ''),
                        "Resolved": task.get('Resolved', ''),
                    })
            messagebox.showinfo("Exported", f"CSV file saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    # ── Export: Highlights ────────────────────────────────────────────────────

    def _export_highlights(self):
        """
        Export a plain-text highlights digest — entries that have a non-empty
        AI summary, presented in a scannable format ideal for quick review.
        """
        if not self._require_results():
            return

        path = self._ask_save_path(
            "Save Highlights",
            ".txt",
            [("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not path:
            return

        keyword = self.keyword_var.get().strip()
        generated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        highlighted = [t for t in self._results if t.get('AI Summary', '').strip()]

        lines = [
            f"HIGHLIGHTS — {keyword}",
            f"Generated: {generated_at}",
            f"Entries with AI summaries: {len(highlighted)} / {len(self._results)} total",
            "=" * 60,
            "",
        ]

        if not highlighted:
            lines.append("No entries with AI summaries were found for this search.")
        else:
            for task in highlighted:
                start_str = task.get('Start Time', '')
                try:
                    dt = datetime.datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
                    stamp = dt.strftime("%Y-%m-%d %H:%M")
                except ValueError:
                    stamp = start_str

                ticket = task.get('Ticket', '') or '(no ticket)'
                title = task.get('Title', '').replace('\n', ' ')
                summary = task.get('AI Summary', '').strip()

                lines.append(f"[{stamp}]  {ticket}")
                lines.append(f"Task: {title}")
                lines.append(f"Summary: {summary}")
                lines.append("-" * 40)
                lines.append("")

        try:
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write('\n'.join(lines))
            messagebox.showinfo("Exported", f"Highlights file saved to:\n{path}")
        except Exception as exc:
            messagebox.showerror("Export Failed", str(exc))

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def refresh(self):
        """Called when navigating to this page — reset to yesterday's date range."""
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        self.from_var.set(yesterday)
        self.to_var.set(today_str)
        self.status_label.config(text="Enter a keyword and press Search")
