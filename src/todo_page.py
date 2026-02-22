"""
Todo List Page - Manage a personal list of tasks to focus on.
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import requests
import theme
from todo_repository import TodoRepository


_PRIORITIES = ("High", "Medium", "Low")


class TodoPage(tk.Frame):
    """Page for managing a personal todo/focus list."""

    def __init__(self, parent, todo_repository: TodoRepository, settings_manager=None):
        """
        Initialize the Todo page.

        Args:
            parent: Parent tkinter widget
            todo_repository: TodoRepository instance
            settings_manager: Optional SettingsManager instance for AI features
        """
        super().__init__(parent, bg=theme.WINDOW_BG)
        self.todo_repository = todo_repository
        self.settings_manager = settings_manager
        self._create_widgets()
        self._load_todos()

    # ── Widget construction ────────────────────────────────────────────────────

    def _create_widgets(self):
        """Create all UI widgets for the todo page."""
        # Header
        tk.Label(
            self, text="Todo List",
            font=theme.FONT_H2, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(anchor='w', padx=10, pady=(10, 5))

        tk.Label(
            self, text="Keep track of the tasks you're concentrating on right now.",
            font=theme.FONT_SMALL, bg=theme.WINDOW_BG, fg=theme.MUTED,
        ).pack(anchor='w', padx=10, pady=(0, 8))

        # Task list
        list_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)

        columns = ('task', 'priority', 'status', 'created')
        self.todo_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

        self.todo_tree.heading('task', text='Task')
        self.todo_tree.heading('priority', text='Priority')
        self.todo_tree.heading('status', text='Status')
        self.todo_tree.heading('created', text='Created')

        self.todo_tree.column('task', width=350)
        self.todo_tree.column('priority', width=80)
        self.todo_tree.column('status', width=80)
        self.todo_tree.column('created', width=130)

        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.todo_tree.yview)
        self.todo_tree.configure(yscrollcommand=scrollbar.set)

        self.todo_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Bind double-click to toggle status
        self.todo_tree.bind('<Double-1>', self._on_double_click)

        # Action buttons
        btn_frame = tk.Frame(self, bg=theme.WINDOW_BG)
        btn_frame.pack(fill='x', padx=10, pady=8)

        tk.Button(
            btn_frame, text="Add Task", command=self._add_todo,
            bg=theme.PRIMARY, fg=theme.TEXT,
            font=theme.FONT_BODY_BOLD, width=12, relief='flat', cursor='hand2',
            padx=8, pady=4,
        ).pack(side='left', padx=4)

        tk.Button(
            btn_frame, text="Mark Done", command=self._mark_done,
            bg=theme.GREEN, fg=theme.WINDOW_BG,
            font=theme.FONT_BODY, width=12, relief='flat', cursor='hand2',
            padx=8, pady=4,
        ).pack(side='left', padx=4)

        tk.Button(
            btn_frame, text="Mark Pending", command=self._mark_pending,
            bg=theme.ACCENT, fg=theme.WINDOW_BG,
            font=theme.FONT_BODY, width=12, relief='flat', cursor='hand2',
            padx=8, pady=4,
        ).pack(side='left', padx=4)

        tk.Button(
            btn_frame, text="Delete", command=self._delete_todo,
            bg=theme.RED, fg=theme.TEXT,
            font=theme.FONT_BODY, width=12, relief='flat', cursor='hand2',
            padx=8, pady=4,
        ).pack(side='left', padx=4)

        tk.Button(
            btn_frame, text="AI Suggest Order", command=self._ai_suggest_order,
            bg=theme.ACCENT, fg=theme.WINDOW_BG,
            font=theme.FONT_BODY, width=16, relief='flat', cursor='hand2',
            padx=8, pady=4,
        ).pack(side='left', padx=4)

        # Status bar
        self.status_label = tk.Label(
            self, text="",
            font=theme.FONT_SMALL, bg=theme.WINDOW_BG, fg=theme.MUTED,
        )
        self.status_label.pack(pady=4)

    # ── Data loading ───────────────────────────────────────────────────────────

    def _load_todos(self):
        """Load all todos from the repository and populate the tree."""
        for item in self.todo_tree.get_children():
            self.todo_tree.delete(item)

        todos = self.todo_repository.get_all_todos()
        for todo in todos:
            self.todo_tree.insert(
                '', 'end',
                iid=todo.get('ID'),
                values=(
                    todo.get('Task', ''),
                    todo.get('Priority', ''),
                    todo.get('Status', ''),
                    todo.get('Created', ''),
                ),
            )

        pending = sum(1 for t in todos if t.get('Status') == 'Pending')
        self.status_label.config(
            text=f"{len(todos)} item(s) total — {pending} pending"
        )

    # ── Event handlers ─────────────────────────────────────────────────────────

    def _on_double_click(self, _event):
        """Toggle status on double-click."""
        selection = self.todo_tree.selection()
        if not selection:
            return
        todo_id = selection[0]
        current_status = self.todo_tree.item(todo_id)['values'][2]
        new_status = "Pending" if current_status == "Done" else "Done"
        self._set_status(todo_id, new_status)

    def _add_todo(self):
        """Open a dialog to add a new todo item."""
        dialog = tk.Toplevel(self)
        dialog.title("Add Todo Task")
        dialog.geometry("420x250")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(bg=theme.WINDOW_BG)

        tk.Label(
            dialog, text="Task description:",
            font=theme.FONT_BODY_BOLD, bg=theme.WINDOW_BG, fg=theme.TEXT, anchor='w',
        ).pack(fill='x', padx=15, pady=(15, 2))

        task_var = tk.StringVar()
        task_entry = tk.Entry(
            dialog, textvariable=task_var,
            font=theme.FONT_BODY, bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief='flat',
        )
        task_entry.pack(fill='x', padx=15, pady=(0, 10))

        tk.Label(
            dialog, text="Priority:",
            font=theme.FONT_BODY_BOLD, bg=theme.WINDOW_BG, fg=theme.TEXT, anchor='w',
        ).pack(fill='x', padx=15, pady=(0, 2))

        priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(
            dialog, textvariable=priority_var,
            values=list(_PRIORITIES), state='readonly', width=12,
        )
        priority_combo.pack(anchor='w', padx=15, pady=(0, 10))

        tk.Label(
            dialog, text="Notes (optional):",
            font=theme.FONT_BODY_BOLD, bg=theme.WINDOW_BG, fg=theme.TEXT, anchor='w',
        ).pack(fill='x', padx=15, pady=(0, 2))

        notes_var = tk.StringVar()
        tk.Entry(
            dialog, textvariable=notes_var,
            font=theme.FONT_BODY, bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT, relief='flat',
        ).pack(fill='x', padx=15, pady=(0, 10))

        result = {"ok": False}

        def on_ok():
            task = task_var.get().strip()
            if not task:
                messagebox.showwarning("Input Required", "Please enter a task description.", parent=dialog)
                return
            result["task"] = task
            result["priority"] = priority_var.get()
            result["notes"] = notes_var.get().strip()
            result["ok"] = True
            dialog.destroy()

        btn_frame = tk.Frame(dialog, bg=theme.WINDOW_BG)
        btn_frame.pack(pady=6)
        tk.Button(
            btn_frame, text="Add", command=on_ok,
            bg=theme.GREEN, fg=theme.WINDOW_BG,
            font=theme.FONT_BODY, width=10, relief='flat', cursor='hand2',
        ).pack(side='left', padx=5)
        tk.Button(
            btn_frame, text="Cancel", command=dialog.destroy,
            bg=theme.SURFACE_BG, fg=theme.TEXT,
            font=theme.FONT_BODY, width=10, relief='flat', cursor='hand2',
        ).pack(side='left', padx=5)

        task_entry.focus_set()
        self.wait_window(dialog)

        if result.get("ok"):
            if self.todo_repository.add_todo(result["task"], result["priority"], result["notes"]):
                self._load_todos()
                self.status_label.config(text="Task added.")
            else:
                messagebox.showerror("Error", "Failed to add task.")

    def _mark_done(self):
        """Mark selected item(s) as Done."""
        self._update_selected_status("Done")

    def _mark_pending(self):
        """Mark selected item(s) as Pending."""
        self._update_selected_status("Pending")

    def _update_selected_status(self, status: str):
        """Update the status of all selected items."""
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select one or more tasks to update.")
            return
        for todo_id in selection:
            self._set_status(todo_id, status)

    def _set_status(self, todo_id: str, status: str):
        """Set the status of a single item and refresh the tree row."""
        if self.todo_repository.update_todo_status(todo_id, status):
            values = list(self.todo_tree.item(todo_id)['values'])
            values[2] = status
            self.todo_tree.item(todo_id, values=values)
            self.status_label.config(text=f"Task marked as {status}.")
        else:
            messagebox.showerror("Error", "Failed to update task status.")

    def _delete_todo(self):
        """Delete selected todo item(s) after confirmation."""
        selection = self.todo_tree.selection()
        if not selection:
            messagebox.showinfo("No Selection", "Please select one or more tasks to delete.")
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete {len(selection)} task(s)?"):
            return
        for todo_id in selection:
            if self.todo_repository.delete_todo(todo_id):
                self.todo_tree.delete(todo_id)
        self._load_todos()

    # ── AI suggestion ──────────────────────────────────────────────────────────

    def _ai_suggest_order(self):
        """Ask the AI to suggest a completion order for pending tasks."""
        if self.settings_manager is None:
            messagebox.showinfo(
                "AI Not Available",
                "AI features are not configured. Please check settings.",
            )
            return

        todos = self.todo_repository.get_all_todos()
        pending = [t for t in todos if t.get('Status') == 'Pending']

        if not pending:
            messagebox.showinfo("No Pending Tasks", "There are no pending tasks to order.")
            return

        # Build the task list string for the prompt
        task_lines = []
        for i, t in enumerate(pending, start=1):
            notes = t.get('Notes', '').strip()
            note_part = f" — Notes: {notes}" if notes else ""
            task_lines.append(
                f"{i}. [{t.get('Priority', 'Medium')}] {t.get('Task', '')}{note_part}"
            )
        task_list_str = "\n".join(task_lines)

        prompt = (
            "You are a productivity assistant helping someone prioritise their work.\n"
            "Below is a list of pending tasks with their priorities and any notes.\n\n"
            f"{task_list_str}\n\n"
            "Please suggest the best order to tackle these tasks and briefly explain "
            "your reasoning for each placement. Consider urgency implied by priority, "
            "dependencies, and logical groupings. Format your response clearly with a "
            "numbered list followed by a short explanation."
        )

        # Show a 'thinking' dialog while the AI works
        thinking_win = tk.Toplevel(self)
        thinking_win.title("AI Suggestion")
        thinking_win.geometry("320x100")
        thinking_win.transient(self)
        thinking_win.configure(bg=theme.WINDOW_BG)
        tk.Label(
            thinking_win,
            text="Asking AI for a suggested order…",
            font=theme.FONT_BODY, bg=theme.WINDOW_BG, fg=theme.TEXT,
            wraplength=280,
        ).pack(expand=True, pady=20)

        def _run():
            result = self._call_ai(prompt)
            self.after(0, lambda: self._show_ai_result(result, thinking_win))

        threading.Thread(target=_run).start()

    def _call_ai(self, prompt: str) -> str:
        """Send *prompt* to the configured LLM and return the response text."""
        payload = {
            "model": self.settings_manager.get("ai_model"),
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = requests.post(
                self.settings_manager.get("ai_api_url"),
                json=payload,
                timeout=self.settings_manager.get("llm_request_timeout"),
            )
            if response.status_code == 200:
                text = response.json().get("response", "").strip()
                return text if text else "AI returned an empty response. Please try again."
            return f"Error: HTTP {response.status_code}"
        except requests.exceptions.Timeout:
            return "AI request timed out. Please try again or check your timeout settings."
        except Exception as e:
            return f"AI connection failed: {e}"

    def _show_ai_result(self, result: str, thinking_win: tk.Toplevel):
        """Close the thinking dialog and display the AI suggestion."""
        thinking_win.destroy()

        win = tk.Toplevel(self)
        win.title("AI Suggested Task Order")
        win.geometry("600x480")
        win.transient(self)
        win.configure(bg=theme.WINDOW_BG)

        tk.Label(
            win, text="AI Suggested Order",
            font=theme.FONT_H2, bg=theme.WINDOW_BG, fg=theme.TEXT,
        ).pack(pady=(12, 4))

        tk.Label(
            win,
            text="Here is the AI's suggested order for your pending tasks:",
            font=theme.FONT_SMALL, bg=theme.WINDOW_BG, fg=theme.MUTED,
        ).pack(pady=(0, 6))

        text_area = scrolledtext.ScrolledText(
            win, wrap=tk.WORD,
            font=theme.FONT_BODY,
            bg=theme.INPUT_BG, fg=theme.TEXT,
            insertbackground=theme.TEXT,
            relief='flat', padx=8, pady=6,
            state='normal',
        )
        text_area.pack(fill='both', expand=True, padx=12, pady=4)
        text_area.insert('1.0', result)
        text_area.config(state='disabled')

        tk.Button(
            win, text="Close", command=win.destroy,
            bg=theme.SURFACE_BG, fg=theme.TEXT,
            font=theme.FONT_BODY, width=12, relief='flat', cursor='hand2',
        ).pack(pady=10)

    # ── Public API ─────────────────────────────────────────────────────────────

    def refresh(self):
        """Refresh the page (called when navigating to this page)."""
        self._load_todos()
