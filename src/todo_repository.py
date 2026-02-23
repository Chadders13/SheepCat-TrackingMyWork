"""
CSV-based repository for personal todo items.
"""
import csv
import os
import re
import datetime
from typing import List, Dict, Optional


def extract_due_date(task_text: str) -> str:
    """Try to extract a due date/time from free-text task description.

    Looks for common time expressions (e.g. "by 3pm", "before noon",
    "due tomorrow at 14:00") and returns a formatted string
    ``"YYYY-MM-DD HH:MM"`` or ``"YYYY-MM-DD"``.  Returns ``""`` if nothing
    is found.
    """
    text = task_text.lower()
    today = datetime.date.today()
    target_date = today + datetime.timedelta(days=1) if "tomorrow" in text else today

    # Named time shortcuts (ordered longest-first to avoid partial matches)
    named_times = [
        ("end of day", datetime.time(17, 0)),
        ("eod",        datetime.time(17, 0)),
        ("noon",       datetime.time(12, 0)),
        ("midnight",   datetime.time(0, 0)),
        ("morning",    datetime.time(9, 0)),
        ("afternoon",  datetime.time(14, 0)),
        ("evening",    datetime.time(18, 0)),
    ]
    for name, t in named_times:
        if name in text:
            return datetime.datetime.combine(target_date, t).strftime("%Y-%m-%d %H:%M")

    # HH:MM am/pm  (e.g. "3:30pm", "11:00 AM")
    m = re.search(r'\b(\d{1,2}):(\d{2})\s*(am|pm)\b', text)
    if m:
        h, mins, ampm = int(m.group(1)), int(m.group(2)), m.group(3)
        if ampm == 'pm' and h != 12:
            h += 12
        elif ampm == 'am' and h == 12:
            h = 0
        try:
            return datetime.datetime.combine(target_date, datetime.time(h, mins)).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass

    # H am/pm  (e.g. "3pm", "11 AM")
    m = re.search(r'\b(\d{1,2})\s*(am|pm)\b', text)
    if m:
        h, ampm = int(m.group(1)), m.group(2)
        if ampm == 'pm' and h != 12:
            h += 12
        elif ampm == 'am' and h == 12:
            h = 0
        try:
            return datetime.datetime.combine(target_date, datetime.time(h, 0)).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass

    # 24-hour HH:MM  (e.g. "14:00", "09:30")
    m = re.search(r'\b([01]?\d|2[0-3]):([0-5]\d)\b', text)
    if m:
        h, mins = int(m.group(1)), int(m.group(2))
        try:
            return datetime.datetime.combine(target_date, datetime.time(h, mins)).strftime("%Y-%m-%d %H:%M")
        except ValueError:
            pass

    # Plain "today" / "tomorrow" with no specific time
    if "today" in text or "tomorrow" in text:
        return target_date.strftime("%Y-%m-%d")

    return ""



class TodoRepository:
    """CSV file-based repository for personal todo items."""

    HEADERS = ["ID", "Task", "Priority", "Status", "Created", "Notes", "DueDate"]

    def __init__(self, csv_file_path: str):
        """
        Initialize the Todo repository.

        Args:
            csv_file_path: Path to the todo CSV file
        """
        self.csv_file_path = csv_file_path

    def initialize(self):
        """Create the CSV file with headers if it doesn't exist.

        If the file exists but is missing the DueDate column, the column is
        added to both the header and every existing row (with an empty value).
        """
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.HEADERS)
            return

        # Migrate existing file: add DueDate column if absent
        rows = self._read_rows()
        if rows and "DueDate" not in rows[0]:
            rows[0].append("DueDate")
            for row in rows[1:]:
                if row:
                    row.append("")
            self._write_rows(rows)

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _read_rows(self) -> List[List[str]]:
        """Return all raw rows (including header) from the CSV file."""
        if not os.path.exists(self.csv_file_path):
            return [list(self.HEADERS)]
        with open(self.csv_file_path, mode='r', encoding='utf-8') as f:
            return list(csv.reader(f))

    def _write_rows(self, rows: List[List[str]]):
        """Write all rows back to the CSV file."""
        with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerows(rows)

    def _next_id(self, rows: List[List[str]]) -> str:
        """Return the next available integer ID as a string."""
        ids = []
        for row in rows[1:]:  # skip header
            if row:
                try:
                    ids.append(int(row[0]))
                except ValueError:
                    pass
        return str(max(ids) + 1) if ids else "1"

    # ── Public API ─────────────────────────────────────────────────────────────

    def add_todo(self, task: str, priority: str = "Medium", notes: str = "",
                 due_date: str = "") -> bool:
        """
        Add a new todo item.

        Args:
            task: Description of the task
            priority: Priority level ("High", "Medium", or "Low")
            notes: Optional extra notes
            due_date: Optional due date/time string (e.g. "2024-01-20 14:00")

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows = self._read_rows()
            todo_id = self._next_id(rows)
            created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [todo_id, task, priority, "Pending", created, notes, due_date]
            with open(self.csv_file_path, mode='a', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(new_row)
            return True
        except Exception as e:
            print(f"Error adding todo: {e}")
            return False

    def get_all_todos(self) -> List[Dict]:
        """
        Get all todo items.

        Returns:
            List of todo dictionaries
        """
        todos = []
        try:
            with open(self.csv_file_path, mode='r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    todos.append(dict(row))
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error reading todos: {e}")
        return todos

    def update_todo_status(self, todo_id: str, status: str) -> bool:
        """
        Update the status of a todo item.

        Args:
            todo_id: The ID of the todo item
            status: New status ("Pending" or "Done")

        Returns:
            bool: True if found and updated, False otherwise
        """
        try:
            rows = self._read_rows()
            updated = False
            for i, row in enumerate(rows):
                if i == 0:
                    continue  # skip header
                if row and row[0] == todo_id:
                    rows[i][3] = status  # Status is column index 3
                    updated = True
                    break
            if updated:
                self._write_rows(rows)
            return updated
        except Exception as e:
            print(f"Error updating todo status: {e}")
            return False

    def delete_todo(self, todo_id: str) -> bool:
        """
        Delete a todo item by ID.

        Args:
            todo_id: The ID of the todo item to delete

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows = self._read_rows()
            new_rows = [rows[0]] + [r for r in rows[1:] if r and r[0] != todo_id]
            self._write_rows(new_rows)
            return True
        except Exception as e:
            print(f"Error deleting todo: {e}")
            return False

    def get_due_todos(self, window_minutes: int = 60) -> List[Dict]:
        """
        Return pending todos whose due date falls within the next *window_minutes*
        or that are already overdue.

        Date-only values (format ``YYYY-MM-DD``, without an explicit time) are
        treated as due at 23:59 on that day, so a task set to "complete by
        today" will appear in reminders throughout the entire day.

        Args:
            window_minutes: How many minutes into the future to look.

        Returns:
            List of todo dicts that are pending and due soon / overdue.
        """
        now = datetime.datetime.now()
        cutoff = now + datetime.timedelta(minutes=window_minutes)
        due = []
        for todo in self.get_all_todos():
            if todo.get('Status') == 'Done':
                continue
            raw = todo.get('DueDate', '').strip()
            if not raw:
                continue
            # Try parsing with time first, then date-only
            for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
                try:
                    due_dt = datetime.datetime.strptime(raw, fmt)
                    # For date-only values treat end-of-day as the deadline
                    if fmt == "%Y-%m-%d":
                        due_dt = due_dt.replace(hour=23, minute=59)
                    if due_dt <= cutoff:
                        due.append(todo)
                    break
                except ValueError:
                    continue
        return due
