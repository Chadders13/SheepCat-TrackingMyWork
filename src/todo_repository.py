"""
CSV-based repository for personal todo items.
"""
import csv
import os
import datetime
from typing import List, Dict


# Human-readable day names indexed by Python weekday (0 = Monday)
WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class TodoRepository:
    """CSV file-based repository for personal todo items."""

    HEADERS = ["ID", "Task", "Priority", "Status", "Created", "Notes", "Repeat", "Days", "CommittedAt"]

    def __init__(self, csv_file_path: str):
        """
        Initialize the Todo repository.

        Args:
            csv_file_path: Path to the todo CSV file
        """
        self.csv_file_path = csv_file_path

    def initialize(self):
        """Create the CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, mode='w', newline='', encoding='utf-8') as f:
                csv.writer(f).writerow(self.HEADERS)

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

    def _pad_row(self, row: List[str]) -> List[str]:
        """Ensure a data row has an entry for every column (backward compat)."""
        return row + [""] * (len(self.HEADERS) - len(row))

    # ── Public API ─────────────────────────────────────────────────────────────

    def archive_done_todos(self, archive_file_path: str) -> int:
        """
        Move all Done todos to the archive file and remove them from the active list.

        The archive file is a Markdown document; each completed todo is appended as
        a list item under a dated heading so the file grows over time.

        Args:
            archive_file_path: Path to the Markdown archive/achievements file.

        Returns:
            int: Number of todos archived (0 if none were done).
        """
        try:
            rows = self._read_rows()
            done_rows = [r for r in rows[1:] if r and r[3] == "Done"]
            if not done_rows:
                return 0

            # Append to the archive file
            date_heading = datetime.datetime.now().strftime("%Y-%m-%d")
            parent_dir = os.path.dirname(archive_file_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            with open(archive_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n## {date_heading}\n\n")
                for r in done_rows:
                    task = r[1] if len(r) > 1 else ""
                    priority = r[2] if len(r) > 2 else ""
                    created = r[4] if len(r) > 4 else ""
                    notes = r[5] if len(r) > 5 else ""
                    line = f"- [x] **{task}** (Priority: {priority}, Created: {created})"
                    if notes:
                        line += f" — {notes}"
                    f.write(line + "\n")

            # Remove done rows from the active list
            done_ids = {r[0] for r in done_rows}
            kept = [rows[0]] + [r for r in rows[1:] if r and r[0] not in done_ids]
            self._write_rows(kept)

            return len(done_rows)
        except Exception as e:
            print(f"Error archiving done todos: {e}")
            return 0

    def add_todo(self, task: str, priority: str = "Medium", notes: str = "") -> bool:
        """
        Add a new todo item.

        Args:
            task: Description of the task
            priority: Priority level ("High", "Medium", or "Low")
            notes: Optional extra notes
            repeat: Recurrence rule – "none", "daily", or "specific_days"
            days: Comma-separated weekday integers (0=Mon … 6=Sun) used when
                  repeat is "specific_days"

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            rows = self._read_rows()
            todo_id = self._next_id(rows)
            created = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_row = [todo_id, task, priority, "Pending", created, notes, repeat, days, ""]
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
                    rows[i] = self._pad_row(rows[i])
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

    def get_todos_due_today(self) -> List[Dict]:
        """
        Return todos whose recurrence schedule includes today.

        A todo is *due today* when:
        - ``Repeat`` is ``"daily"`` — appears every day.
        - ``Repeat`` is ``"specific_days"`` and today's weekday (0 = Monday)
          is listed in the ``Days`` column.

        Todos with ``Repeat`` equal to ``"none"`` or empty are not returned.

        Returns:
            List of todo dictionaries due today (any status).
        """
        today_weekday = datetime.date.today().weekday()
        due = []
        for todo in self.get_all_todos():
            repeat = todo.get('Repeat', 'none') or 'none'
            if repeat == 'daily':
                due.append(todo)
            elif repeat == 'specific_days':
                days_str = todo.get('Days', '') or ''
                days = [int(d.strip()) for d in days_str.split(',') if d.strip().isdigit()]
                if today_weekday in days:
                    due.append(todo)
        return due

    def set_committed(self, todo_id: str) -> bool:
        """
        Mark a todo as committed to by the next check-in.

        Sets the ``CommittedAt`` column to the current datetime.

        Args:
            todo_id: The ID of the todo item

        Returns:
            bool: True if found and updated, False otherwise
        """
        _committed_idx = self.HEADERS.index('CommittedAt')
        try:
            rows = self._read_rows()
            committed_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            updated = False
            for i, row in enumerate(rows):
                if i == 0:
                    continue
                if row and row[0] == todo_id:
                    rows[i] = self._pad_row(rows[i])
                    rows[i][_committed_idx] = committed_at
                    updated = True
                    break
            if updated:
                self._write_rows(rows)
            return updated
        except Exception as e:
            print(f"Error setting committed: {e}")
            return False

    def clear_committed(self, todo_id: str) -> bool:
        """
        Clear the committed flag on a todo item.

        Args:
            todo_id: The ID of the todo item

        Returns:
            bool: True if found and updated, False otherwise
        """
        _committed_idx = self.HEADERS.index('CommittedAt')
        try:
            rows = self._read_rows()
            updated = False
            for i, row in enumerate(rows):
                if i == 0:
                    continue
                if row and row[0] == todo_id:
                    rows[i] = self._pad_row(rows[i])
                    rows[i][_committed_idx] = ""
                    updated = True
                    break
            if updated:
                self._write_rows(rows)
            return updated
        except Exception as e:
            print(f"Error clearing committed: {e}")
            return False

    def get_committed_todos(self) -> List[Dict]:
        """
        Return todos that the user has committed to looking at by the next check-in.

        Returns:
            List of todo dicts where ``CommittedAt`` is non-empty.
        """
        return [t for t in self.get_all_todos() if t.get('CommittedAt', '')]
