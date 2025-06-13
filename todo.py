import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
# Set data file path relative to script location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'todo_data.json')


class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Advanced ToDo List Application")
        self.root.geometry("1200x800")
        
        # Data structures
        self.tasks = []
        self.history = []  # For undo/redo functionality
        self.history_index = -1
        self.statistics = {
            'daily': {},
            'weekly': {},
            'monthly': {},
            'total_done': 0,
            'total_skipped': 0
        }
        
        # Load saved data
        self.load_data()
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
        # Create four sections
        self.create_task_section()
        self.create_statistics_section()
        self.create_daily_chart_section()
        self.create_radar_chart_section()
        
        # Save data when closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Update displays
        self.update_displays()
    
    def create_task_section(self):
        """First section: Task management"""
        task_frame = ttk.LabelFrame(self.main_frame, text="Tasks Management", padding="10")
        task_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        task_frame.columnconfigure(0, weight=1)
        
        # Current task display
        current_task_frame = ttk.Frame(task_frame)
        current_task_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        current_task_frame.columnconfigure(1, weight=1)
        
        ttk.Label(current_task_frame, text="Current Task:").grid(row=0, column=0, sticky=tk.W)
        self.current_task_var = tk.StringVar()
        self.current_task_label = ttk.Label(current_task_frame, textvariable=self.current_task_var, 
                                          font=('Arial', 12, 'bold'))
        self.current_task_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=10)
        
        # Task action buttons
        action_frame = ttk.Frame(task_frame)
        action_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.done_btn = ttk.Button(action_frame, text="Done (Current)", command=self.mark_current_done)
        self.done_btn.grid(row=0, column=0, padx=5)
        
        self.skip_btn = ttk.Button(action_frame, text="Skip (Current)", command=self.mark_current_skip)
        self.skip_btn.grid(row=0, column=1, padx=5)
        
        # NEW: Buttons for selected task
        self.done_selected_btn = ttk.Button(action_frame, text="Done (Selected)", command=self.mark_selected_done)
        self.done_selected_btn.grid(row=0, column=2, padx=5)
        
        self.skip_selected_btn = ttk.Button(action_frame, text="Skip (Selected)", command=self.mark_selected_skip)
        self.skip_selected_btn.grid(row=0, column=3, padx=5)
        
        # Task list
        list_frame = ttk.Frame(task_frame)
        list_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        self.task_listbox = tk.Listbox(list_frame, height=8)
        self.task_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind selection event to update button states
        self.task_listbox.bind('<<ListboxSelect>>', self.on_task_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.task_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.task_listbox.config(yscrollcommand=scrollbar.set)
        
        # Management buttons
        mgmt_frame = ttk.Frame(task_frame)
        mgmt_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(mgmt_frame, text="Add Task", command=self.add_task).grid(row=0, column=0, padx=2)
        ttk.Button(mgmt_frame, text="Edit Task", command=self.edit_task).grid(row=0, column=1, padx=2)
        ttk.Button(mgmt_frame, text="Delete Task", command=self.delete_task).grid(row=0, column=2, padx=2)
        ttk.Button(mgmt_frame, text="Undo", command=self.undo).grid(row=0, column=3, padx=2)
        ttk.Button(mgmt_frame, text="Redo", command=self.redo).grid(row=0, column=4, padx=2)
        ttk.Button(mgmt_frame, text="Save Progress", command=self.save_data).grid(row=0, column=5, padx=2)
        
        task_frame.rowconfigure(2, weight=1)
    
    def create_statistics_section(self):
        """Second section: Statistics"""
        stats_frame = ttk.LabelFrame(self.main_frame, text="Statistics", padding="10")
        stats_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=15, width=30)
        self.stats_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        stats_scrollbar = ttk.Scrollbar(stats_frame, orient=tk.VERTICAL, command=self.stats_text.yview)
        stats_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.stats_text.config(yscrollcommand=stats_scrollbar.set)
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.rowconfigure(0, weight=1)
    
    def create_daily_chart_section(self):
        """Third section: 7-day chart"""
        chart_frame = ttk.LabelFrame(self.main_frame, text="7-Day Performance Chart", padding="10")
        chart_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.fig1, self.ax1 = plt.subplots(figsize=(6, 3))
        self.canvas1 = FigureCanvasTkAgg(self.fig1, chart_frame)
        self.canvas1.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
    
    def create_radar_chart_section(self):
        """Fourth section: Radar chart"""
        radar_frame = ttk.LabelFrame(self.main_frame, text="Task Performance Radar", padding="10")
        radar_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        self.fig2, self.ax2 = plt.subplots(figsize=(6, 3), subplot_kw=dict(projection='polar'))
        self.canvas2 = FigureCanvasTkAgg(self.fig2, radar_frame)
        self.canvas2.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        radar_frame.columnconfigure(0, weight=1)
        radar_frame.rowconfigure(0, weight=1)
    
    def on_task_select(self, event):
        """Handle task selection in listbox"""
        selection = self.task_listbox.curselection()
        if selection:
            self.done_selected_btn.config(state='normal')
            self.skip_selected_btn.config(state='normal')
        else:
            self.done_selected_btn.config(state='disabled')
            self.skip_selected_btn.config(state='disabled')
    
    def save_state(self):
        """Save current state for undo/redo"""
        state = {
            'tasks': self.tasks.copy(),
            'statistics': self.statistics.copy()
        }
        
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        self.history.append(state)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > 50:
            self.history.pop(0)
            self.history_index -= 1
    
    def add_task(self):
        """Add new task"""
        task = simpledialog.askstring("Add Task", "Enter task description:")
        if task:
            self.save_state()
            # Find the next available task ID (A, B, C, etc.)
            existing_ids = set()
            for t in self.tasks:
                if 'task_id' in t:
                    existing_ids.add(t['task_id'])
            
            # Find first available letter
            task_id = None
            for i in range(26):  # A-Z
                candidate_id = chr(65 + i)  # A, B, C, ...
                if candidate_id not in existing_ids:
                    task_id = candidate_id
                    break
            
            # If all letters used, use Task1, Task2, etc.
            if task_id is None:
                counter = 1
                while f"Task{counter}" in existing_ids:
                    counter += 1
                task_id = f"Task{counter}"
            
            task_data = {
                'task_id': task_id,
                'description': task,
                'created': datetime.now().isoformat(),
                'completed_count': 0,
                'skipped_count': 0
            }
            self.tasks.append(task_data)
            self.update_displays()
    
    def edit_task(self):
        """Edit selected task"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to edit")
            return
        
        index = selection[0]
        current_desc = self.tasks[index]['description']
        new_desc = simpledialog.askstring("Edit Task", "Enter new description:", initialvalue=current_desc)
        
        if new_desc:
            self.save_state()
            self.tasks[index]['description'] = new_desc
            self.update_displays()
    
    def delete_task(self):
        """Delete selected task"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to delete")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this task?"):
            self.save_state()
            index = selection[0]
            self.tasks.pop(index)
            self.update_displays()
    
    def mark_current_done(self):
        """Mark current (first) task as done and move to end"""
        if not self.tasks:
            return
        
        self.save_state()
        task = self.tasks.pop(0)
        task['completed_count'] += 1
        self.tasks.append(task)
        
        # Update statistics
        today = datetime.now().strftime('%Y-%m-%d')
        self.statistics['daily'][today] = self.statistics['daily'].get(today, 0) + 1
        self.statistics['total_done'] += 1
        
        self.update_displays()
    
    def mark_current_skip(self):
        """Mark current (first) task as skipped and move to end"""
        if not self.tasks:
            return
        
        self.save_state()
        task = self.tasks.pop(0)
        task['skipped_count'] += 1
        self.tasks.append(task)
        
        # Update statistics
        self.statistics['total_skipped'] += 1
        
        self.update_displays()
    
    def mark_selected_done(self):
        """Mark selected task as done and move to end"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to mark as done")
            return
        
        self.save_state()
        index = selection[0]
        task = self.tasks.pop(index)
        task['completed_count'] += 1
        self.tasks.append(task)
        
        # Update statistics
        today = datetime.now().strftime('%Y-%m-%d')
        self.statistics['daily'][today] = self.statistics['daily'].get(today, 0) + 1
        self.statistics['total_done'] += 1
        
        self.update_displays()
    
    def mark_selected_skip(self):
        """Mark selected task as skipped and move to end"""
        selection = self.task_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a task to mark as skipped")
            return
        
        self.save_state()
        index = selection[0]
        task = self.tasks.pop(index)
        task['skipped_count'] += 1
        self.tasks.append(task)
        
        # Update statistics
        self.statistics['total_skipped'] += 1
        
        self.update_displays()
    
    # Keep the old methods for backward compatibility
    def mark_done(self):
        """Alias for mark_current_done"""
        self.mark_current_done()
    
    def mark_skip(self):
        """Alias for mark_current_skip"""
        self.mark_current_skip()
    
    def undo(self):
        """Undo last action"""
        if self.history_index > 0:
            self.history_index -= 1
            state = self.history[self.history_index]
            self.tasks = state['tasks'].copy()
            self.statistics = state['statistics'].copy()
            self.update_displays()
    
    def redo(self):
        """Redo last undone action"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            state = self.history[self.history_index]
            self.tasks = state['tasks'].copy()
            self.statistics = state['statistics'].copy()
            self.update_displays()
    
    def update_displays(self):
        """Update all display elements"""
        self.update_task_display()
        self.update_statistics_display()
        self.update_daily_chart()
        self.update_individual_task_chart()
    
    def update_task_display(self):
        """Update task list and current task"""
        # Update current task
        if self.tasks:
            current_task = self.tasks[0]
            task_id = current_task.get('task_id', 'Unknown')
            completed = current_task.get('completed_count', 0)
            self.current_task_var.set(f"{task_id} - {current_task['description']} (Done: {completed})")
            self.done_btn.config(state='normal')
            self.skip_btn.config(state='normal')
        else:
            self.current_task_var.set("No tasks available")
            self.done_btn.config(state='disabled')
            self.skip_btn.config(state='disabled')
        
        # Update task list
        self.task_listbox.delete(0, tk.END)
        for task in self.tasks:
            task_id = task.get('task_id', 'Unknown')
            completed = task.get('completed_count', 0)
            skipped = task.get('skipped_count', 0)
            self.task_listbox.insert(tk.END, f"{task_id}: {task['description']} (✓{completed}, ✗{skipped})")
        
        # Update selected task button states
        selection = self.task_listbox.curselection()
        if selection and self.tasks:
            self.done_selected_btn.config(state='normal')
            self.skip_selected_btn.config(state='normal')
        else:
            self.done_selected_btn.config(state='disabled')
            self.skip_selected_btn.config(state='disabled')
    
    def update_statistics_display(self):
        """Update statistics text"""
        self.stats_text.delete(1.0, tk.END)
        
        # Calculate averages
        daily_avg = self.calculate_daily_average()
        weekly_avg = self.calculate_weekly_average()
        monthly_avg = self.calculate_monthly_average()
        
        stats_text = f"""STATISTICS (Done Tasks Only)

Daily Average: {daily_avg:.2f} tasks/day
Weekly Average: {weekly_avg:.2f} tasks/week
Monthly Average: {monthly_avg:.2f} tasks/month

Total Completed: {self.statistics['total_done']}
Total Skipped: {self.statistics['total_skipped']}

INDIVIDUAL TASK COMPLETION COUNTS:
"""
        
        # Show individual task completion counts (sorted by task_id)
        sorted_tasks = sorted(self.tasks, key=lambda x: x.get('task_id', 'ZZZ'))
        for task in sorted_tasks:
            task_id = task.get('task_id', 'Unknown')
            completed = task['completed_count']
            skipped = task['skipped_count']
            total = completed + skipped
            rate = (completed / total * 100) if total > 0 else 0
            stats_text += f"{task_id} ({task['description'][:20]}...): {completed} done, {skipped} skip ({rate:.0f}% success)\n"
        
        stats_text += f"""
Recent Daily Counts:
"""
        
        # Show last 7 days
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            count = self.statistics['daily'].get(date, 0)
            day_name = (datetime.now() - timedelta(days=i)).strftime('%A')
            stats_text += f"{day_name} ({date}): {count} tasks\n"
        
        self.stats_text.insert(1.0, stats_text)
    
    def calculate_daily_average(self):
        """Calculate daily average for last 30 days"""
        if not self.statistics['daily']:
            return 0.0
        
        total = 0
        days = 0
        for i in range(30):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            if date in self.statistics['daily']:
                total += self.statistics['daily'][date]
                days += 1
        
        return total / max(days, 1)
    
    def calculate_weekly_average(self):
        """Calculate weekly average"""
        return self.calculate_daily_average() * 7
    
    def calculate_monthly_average(self):
        """Calculate monthly average"""
        return self.calculate_daily_average() * 30
    
    def update_daily_chart(self):
        """Update 7-day performance chart"""
        self.ax1.clear()
        
        days = []
        counts = []
        
        for i in range(6, -1, -1):  # Last 7 days
            date = datetime.now() - timedelta(days=i)
            day_name = date.strftime('%a')
            date_str = date.strftime('%Y-%m-%d')
            count = self.statistics['daily'].get(date_str, 0)
            
            days.append(day_name)
            counts.append(count)
        
        if counts:
            max_count = max(counts)
            min_count = min(counts)
            avg_count = sum(counts) / len(counts)
            
            colors = []
            for count in counts:
                if count == max_count and max_count > 0:
                    colors.append('green')
                elif count == min_count:
                    colors.append('red')
                else:
                    colors.append('blue')
            
            bars = self.ax1.bar(days, counts, color=colors)
            self.ax1.axhline(y=avg_count, color='blue', linestyle='--', alpha=0.7, label=f'Avg: {avg_count:.1f}')
            
            self.ax1.set_title('7-Day Task Completion')
            self.ax1.set_ylabel('Tasks Completed')
            self.ax1.legend()
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                self.ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                             f'{int(count)}', ha='center', va='bottom')
        
        self.fig1.tight_layout()
        self.canvas1.draw()
    
    def update_individual_task_chart(self):
        """Update individual task completion chart (bar chart instead of radar)"""
        self.ax2.clear()
        
        if not self.tasks:
            self.ax2.text(0.5, 0.5, 'No tasks available', transform=self.ax2.transAxes, 
                         ha='center', va='center')
            self.canvas2.draw()
            return
        
        # Sort tasks by task_id for consistent order (A, B, C, D...)
        sorted_tasks = sorted(self.tasks, key=lambda x: x.get('task_id', 'ZZZ'))
        
        # Prepare data for bar chart
        task_ids = []
        completion_counts = []
        skip_counts = []
        
        for task in sorted_tasks:
            task_ids.append(task.get('task_id', 'Unknown'))
            completion_counts.append(task['completed_count'])
            skip_counts.append(task['skipped_count'])
        
        if len(task_ids) > 0:
            x = np.arange(len(task_ids))
            width = 0.35
            
            # Create bars
            bars1 = self.ax2.bar(x - width/2, completion_counts, width, 
                               label='Completed', color='green', alpha=0.7)
            bars2 = self.ax2.bar(x + width/2, skip_counts, width, 
                               label='Skipped', color='red', alpha=0.7)
            
            # Add value labels on bars
            for bar in bars1:
                height = bar.get_height()
                if height > 0:
                    self.ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                 f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            for bar in bars2:
                height = bar.get_height()
                if height > 0:
                    self.ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                 f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            self.ax2.set_xlabel('Tasks')
            self.ax2.set_ylabel('Count')
            self.ax2.set_title('Individual Task Completion Counts')
            self.ax2.set_xticks(x)
            self.ax2.set_xticklabels(task_ids)
            self.ax2.legend()
            self.ax2.grid(axis='y', alpha=0.3)
            
            # Set y-axis to start from 0
            max_val = max(max(completion_counts) if completion_counts else 0, 
                         max(skip_counts) if skip_counts else 0)
            self.ax2.set_ylim(0, max_val + 1)
        
        self.fig2.tight_layout()
        self.canvas2.draw()
    
    def save_data(self):
        """Save data to file"""
        data = {
            'tasks': self.tasks,
            'statistics': self.statistics
        }
        
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", "Data saved successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save data: {str(e)}")
    
    def load_data(self):
        """Load data from file"""
        try:
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as f:
                    data = json.load(f)
                    self.tasks = data.get('tasks', [])
                    self.statistics = data.get('statistics', {
                        'daily': {},
                        'weekly': {},
                        'monthly': {},
                        'total_done': 0,
                        'total_skipped': 0
                    })
                    
                    # Ensure existing tasks have task_id and completion counts (for backward compatibility)
                    for i, task in enumerate(self.tasks):
                        if 'task_id' not in task:
                            task_id = chr(65 + i) if i < 26 else f"Task{i+1}"
                            task['task_id'] = task_id
                        if 'completed_count' not in task:
                            task['completed_count'] = 0
                        if 'skipped_count' not in task:
                            task['skipped_count'] = 0
                            
        except Exception as e:
            print(f"Failed to load data: {str(e)}")
            self.tasks = []
            self.statistics = {
                'daily': {},
                'weekly': {},
                'monthly': {},
                'total_done': 0,
                'total_skipped': 0
            }
    
    def on_closing(self):
        """Handle application closing"""
        self.save_data()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()