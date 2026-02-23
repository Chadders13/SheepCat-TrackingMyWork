"""
Tests for the data repository implementations.
"""
import os
import sys
import tempfile
import datetime
import unittest

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from csv_data_repository import CSVDataRepository
from todo_repository import TodoRepository


class TestCSVDataRepository(unittest.TestCase):
    def setUp(self):
        """Create a temporary CSV file for testing"""
        # Create a temp file descriptor and close it to get just the path
        fd, self.csv_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        # Remove the file so repository can create it fresh
        os.remove(self.csv_path)
        self.repo = CSVDataRepository(self.csv_path)
    
    def tearDown(self):
        """Clean up temporary file"""
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
    
    def test_initialize_creates_file(self):
        """Test that initialize creates a CSV file with headers"""
        self.repo.initialize()
        self.assertTrue(os.path.exists(self.csv_path))
        
        # Check headers
        with open(self.csv_path, 'r') as f:
            headers = f.readline().strip()
            expected = "Start Time,End Time,Duration (Min),Ticket,Title,System Info,AI Summary,Resolved"
            self.assertEqual(headers, expected)
    
    def test_log_task(self):
        """Test logging a task"""
        self.repo.initialize()
        
        task_data = {
            'start_time': '2024-01-15 10:00:00',
            'end_time': '2024-01-15 10:30:00',
            'duration': 30.0,
            'ticket': 'TEST-123',
            'title': 'Test Task',
            'system_info': 'Test System',
            'ai_summary': 'Task summary',
            'resolved': 'Yes'
        }
        
        result = self.repo.log_task(task_data)
        self.assertTrue(result)
        
        # Verify task was logged
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]['Title'], 'Test Task')
        self.assertEqual(tasks[0]['Ticket'], 'TEST-123')
        self.assertEqual(tasks[0]['Resolved'], 'Yes')
    
    def test_get_tasks_by_date(self):
        """Test retrieving tasks by date"""
        self.repo.initialize()
        
        # Add tasks on different dates
        task1 = {
            'start_time': '2024-01-15 10:00:00',
            'end_time': '2024-01-15 10:30:00',
            'duration': 30.0,
            'ticket': 'TEST-1',
            'title': 'Task 1',
            'system_info': 'Test',
            'ai_summary': 'Summary 1',
            'resolved': 'Yes'
        }
        
        task2 = {
            'start_time': '2024-01-16 11:00:00',
            'end_time': '2024-01-16 11:30:00',
            'duration': 30.0,
            'ticket': 'TEST-2',
            'title': 'Task 2',
            'system_info': 'Test',
            'ai_summary': 'Summary 2',
            'resolved': 'No'
        }
        
        self.repo.log_task(task1)
        self.repo.log_task(task2)
        
        # Get tasks for specific date
        date1 = datetime.date(2024, 1, 15)
        tasks_on_date1 = self.repo.get_tasks_by_date(date1)
        
        self.assertEqual(len(tasks_on_date1), 1)
        self.assertEqual(tasks_on_date1[0]['Title'], 'Task 1')
        
        date2 = datetime.date(2024, 1, 16)
        tasks_on_date2 = self.repo.get_tasks_by_date(date2)
        
        self.assertEqual(len(tasks_on_date2), 1)
        self.assertEqual(tasks_on_date2[0]['Title'], 'Task 2')
    
    def test_update_task_resolved_status(self):
        """Test updating the resolved status of a task"""
        self.repo.initialize()
        
        # Log a task
        task_data = {
            'start_time': '2024-01-15 10:00:00',
            'end_time': '2024-01-15 10:30:00',
            'duration': 30.0,
            'ticket': 'TEST-123',
            'title': 'Test Task',
            'system_info': 'Test System',
            'ai_summary': 'Task summary',
            'resolved': 'No'
        }
        self.repo.log_task(task_data)
        
        # Get the task
        tasks = self.repo.get_all_tasks()
        self.assertEqual(len(tasks), 1)
        task_id = tasks[0]['task_id']
        
        # Update status
        result = self.repo.update_task_resolved_status(task_id, 'Yes')
        self.assertTrue(result)
        
        # Verify update
        tasks = self.repo.get_all_tasks()
        self.assertEqual(tasks[0]['Resolved'], 'Yes')
    
    def test_get_tasks_since(self):
        """Test retrieving tasks since a specific datetime"""
        self.repo.initialize()
        
        # Add tasks at different times
        task1 = {
            'start_time': '2024-01-15 09:00:00',
            'end_time': '2024-01-15 09:30:00',
            'duration': 30.0,
            'ticket': 'TEST-1',
            'title': 'Task 1',
            'system_info': 'Test',
            'ai_summary': 'Summary 1',
            'resolved': 'Yes'
        }
        
        task2 = {
            'start_time': '2024-01-15 10:00:00',
            'end_time': '2024-01-15 10:30:00',
            'duration': 30.0,
            'ticket': 'TEST-2',
            'title': 'Task 2',
            'system_info': 'Test',
            'ai_summary': 'Summary 2',
            'resolved': 'No'
        }
        
        task3 = {
            'start_time': '2024-01-15 11:00:00',
            'end_time': '2024-01-15 11:30:00',
            'duration': 30.0,
            'ticket': 'TEST-3',
            'title': 'Task 3',
            'system_info': 'Test',
            'ai_summary': 'Summary 3',
            'resolved': 'Yes'
        }
        
        self.repo.log_task(task1)
        self.repo.log_task(task2)
        self.repo.log_task(task3)
        
        # Get tasks since 10:00
        since_time = datetime.datetime(2024, 1, 15, 10, 0, 0)
        tasks = self.repo.get_tasks_since(since_time)
        
        self.assertEqual(len(tasks), 2)
        self.assertEqual(tasks[0]['Title'], 'Task 2')
        self.assertEqual(tasks[1]['Title'], 'Task 3')


class TestTodoRepository(unittest.TestCase):
    def setUp(self):
        fd, self.csv_path = tempfile.mkstemp(suffix='.csv')
        os.close(fd)
        os.remove(self.csv_path)
        self.repo = TodoRepository(self.csv_path)

    def tearDown(self):
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)

    def test_initialize_creates_file(self):
        """initialize() should create the CSV with the correct headers."""
        self.repo.initialize()
        self.assertTrue(os.path.exists(self.csv_path))
        with open(self.csv_path, 'r') as f:
            headers = f.readline().strip()
        self.assertEqual(headers, "ID,Task,Priority,Status,Created,Notes,DueDate")

    def test_add_and_get_todos(self):
        """add_todo() should persist items retrievable by get_all_todos()."""
        self.repo.initialize()
        self.repo.add_todo("Fix authentication bug", "High", "Blocking release")
        todos = self.repo.get_all_todos()
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]['Task'], 'Fix authentication bug')
        self.assertEqual(todos[0]['Priority'], 'High')
        self.assertEqual(todos[0]['Status'], 'Pending')
        self.assertEqual(todos[0]['Notes'], 'Blocking release')

    def test_add_multiple_todos_unique_ids(self):
        """Each added todo should receive a unique, incrementing ID."""
        self.repo.initialize()
        self.repo.add_todo("Task A")
        self.repo.add_todo("Task B")
        todos = self.repo.get_all_todos()
        self.assertEqual(len(todos), 2)
        self.assertNotEqual(todos[0]['ID'], todos[1]['ID'])

    def test_update_todo_status(self):
        """update_todo_status() should change a todo's Status field."""
        self.repo.initialize()
        self.repo.add_todo("Write tests")
        todos = self.repo.get_all_todos()
        todo_id = todos[0]['ID']

        result = self.repo.update_todo_status(todo_id, "Done")
        self.assertTrue(result)

        updated = self.repo.get_all_todos()
        self.assertEqual(updated[0]['Status'], 'Done')

    def test_update_nonexistent_todo_returns_false(self):
        """update_todo_status() should return False when the ID is not found."""
        self.repo.initialize()
        result = self.repo.update_todo_status("999", "Done")
        self.assertFalse(result)

    def test_delete_todo(self):
        """delete_todo() should remove the item from the repository."""
        self.repo.initialize()
        self.repo.add_todo("Task to delete")
        todos = self.repo.get_all_todos()
        todo_id = todos[0]['ID']

        result = self.repo.delete_todo(todo_id)
        self.assertTrue(result)

        remaining = self.repo.get_all_todos()
        self.assertEqual(len(remaining), 0)

    def test_delete_preserves_other_todos(self):
        """delete_todo() should only remove the specified item."""
        self.repo.initialize()
        self.repo.add_todo("Keep me")
        self.repo.add_todo("Delete me")
        todos = self.repo.get_all_todos()
        delete_id = todos[1]['ID']

        self.repo.delete_todo(delete_id)

        remaining = self.repo.get_all_todos()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0]['Task'], 'Keep me')

    def test_add_todo_with_due_date(self):
        """add_todo() should persist the due_date field."""
        self.repo.initialize()
        self.repo.add_todo("Submit report", due_date="2099-12-31 17:00")
        todos = self.repo.get_all_todos()
        self.assertEqual(todos[0]['DueDate'], "2099-12-31 17:00")

    def test_add_todo_without_due_date(self):
        """add_todo() should store an empty DueDate when none is supplied."""
        self.repo.initialize()
        self.repo.add_todo("No deadline")
        todos = self.repo.get_all_todos()
        self.assertEqual(todos[0].get('DueDate', ''), '')

    def test_initialize_creates_file_with_due_date_header(self):
        """initialize() should create a CSV that includes the DueDate column."""
        self.repo.initialize()
        with open(self.csv_path, 'r') as f:
            headers = f.readline().strip()
        self.assertIn("DueDate", headers)

    def test_initialize_migrates_existing_file(self):
        """initialize() should add DueDate to a CSV that was created without it."""
        # Write an old-style CSV without DueDate
        with open(self.csv_path, 'w', newline='', encoding='utf-8') as f:
            import csv as _csv
            writer = _csv.writer(f)
            writer.writerow(["ID", "Task", "Priority", "Status", "Created", "Notes"])
            writer.writerow(["1", "Old task", "Low", "Pending", "2024-01-01 09:00:00", ""])
        self.repo.initialize()
        todos = self.repo.get_all_todos()
        self.assertIn('DueDate', todos[0])
        self.assertEqual(todos[0]['DueDate'], '')

    def test_get_due_todos_returns_overdue(self):
        """get_due_todos() should include todos that are past due."""
        self.repo.initialize()
        self.repo.add_todo("Overdue task", due_date="2000-01-01 09:00")
        due = self.repo.get_due_todos(window_minutes=60)
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0]['Task'], 'Overdue task')

    def test_get_due_todos_excludes_done(self):
        """get_due_todos() should not include tasks marked Done."""
        self.repo.initialize()
        self.repo.add_todo("Done task", due_date="2000-01-01 09:00")
        todos = self.repo.get_all_todos()
        self.repo.update_todo_status(todos[0]['ID'], 'Done')
        due = self.repo.get_due_todos(window_minutes=60)
        self.assertEqual(len(due), 0)

    def test_get_due_todos_excludes_far_future(self):
        """get_due_todos() should not include todos due far in the future."""
        self.repo.initialize()
        self.repo.add_todo("Future task", due_date="2099-12-31 23:59")
        due = self.repo.get_due_todos(window_minutes=60)
        self.assertEqual(len(due), 0)

    def test_get_due_todos_no_due_date(self):
        """get_due_todos() should ignore todos without a due date."""
        self.repo.initialize()
        self.repo.add_todo("No deadline task")
        due = self.repo.get_due_todos(window_minutes=60)
        self.assertEqual(len(due), 0)


class TestExtractDueDate(unittest.TestCase):
    """Tests for the extract_due_date helper in todo_repository."""

    def setUp(self):
        from todo_repository import extract_due_date
        self.extract = extract_due_date
        self.today = datetime.date.today().strftime("%Y-%m-%d")
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        self.tomorrow = tomorrow

    def test_am_pm_no_minutes(self):
        result = self.extract("finish the report by 3pm")
        self.assertEqual(result, f"{self.today} 15:00")

    def test_am_pm_with_minutes(self):
        result = self.extract("submit by 10:30 AM")
        self.assertEqual(result, f"{self.today} 10:30")

    def test_24_hour(self):
        result = self.extract("deploy at 14:00")
        self.assertEqual(result, f"{self.today} 14:00")

    def test_named_noon(self):
        result = self.extract("done before noon")
        self.assertEqual(result, f"{self.today} 12:00")

    def test_named_eod(self):
        result = self.extract("complete by EOD")
        self.assertEqual(result, f"{self.today} 17:00")

    def test_named_end_of_day(self):
        result = self.extract("finish by end of day")
        self.assertEqual(result, f"{self.today} 17:00")

    def test_tomorrow(self):
        result = self.extract("do this tomorrow")
        self.assertEqual(result, self.tomorrow)

    def test_tomorrow_with_time(self):
        result = self.extract("meeting tomorrow at 9am")
        self.assertEqual(result, f"{self.tomorrow} 09:00")

    def test_no_time_returns_empty(self):
        result = self.extract("fix the login bug")
        self.assertEqual(result, "")

    def test_today_keyword(self):
        result = self.extract("finish today")
        self.assertEqual(result, self.today)


if __name__ == '__main__':
    unittest.main()
