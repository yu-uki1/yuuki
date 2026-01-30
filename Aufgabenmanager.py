import customtkinter as ctk
import json
import os
from tkinter import simpledialog, messagebox
from datetime import datetime, timedelta
from plyer import notification

# -------------------------------
# CustomTkinter Setup
# -------------------------------
ctk.set_default_color_theme("blue")

# -------------------------------
# JSON Datei laden
# -------------------------------
tasks_file = "tasks.json"

if os.path.exists(tasks_file):
    with open(tasks_file, "r") as f:
        data = json.load(f)
        if isinstance(data, dict):
            tasks = data.get("tasks", [])
            current_theme = data.get("theme", "Light")
        elif isinstance(data, list):
            tasks = data
            current_theme = "Light"
        else:
            tasks = []
            current_theme = "Light"
else:
    tasks = []
    current_theme = "Light"

ctk.set_appearance_mode(current_theme)

# -------------------------------
# Funktionen
# -------------------------------
selected_task_index = None

def save_tasks():
    with open(tasks_file, "w") as f:
        json.dump({"tasks": tasks, "theme": ctk.get_appearance_mode()}, f, indent=4)

def show_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        timeout=10
    )

def check_notifications():
    today = datetime.today().date()
    tomorrow = today + timedelta(days=1)
    for task in tasks:
        if not task.get("due_date"):
            continue
        try:
            due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
        except:
            continue
        if due == today:
            show_notification("Aufgabe fällig heute", f"{task['title']} ist heute fällig!")
        elif due == tomorrow:
            show_notification("Aufgabe morgen fällig", f"{task['title']} ist morgen fällig!")

def refresh_tasks():
    for widget in task_frame.winfo_children():
        widget.destroy()
    for idx, task in enumerate(tasks):
        status = task['status']
        title = task['title']
        due = task['due_date']
        priority = task['priority']
        text = f"[{status}] {title} ({due}) - {priority}"
        if task.get("repeat_weekly"):
            text += " 🔁"  # Symbol für wiederkehrende Aufgabe

        if status == "erledigt":
            color = "#2ecc71"
        elif priority == "hoch":
            color = "#e74c3c"
        elif priority == "mittel":
            color = "#e67e22"
        elif priority == "extrem":
            color = "#ff00bf"
        else:
            color = "#414141"

        btn = ctk.CTkButton(task_frame, text=text, fg_color=color, hover_color="#555555",
                            command=lambda idx=idx: select_task(idx), anchor="w")
        btn.pack(fill="x", pady=2)

def select_task(idx):
    global selected_task_index
    selected_task_index = idx

def add_task():
    global selected_task_index
    title = simpledialog.askstring("Aufgabe hinzufügen", "Titel:")
    if not title: return
    description = simpledialog.askstring("Aufgabe hinzufügen", "Beschreibung:")
    due_date = simpledialog.askstring("Aufgabe hinzufügen", "Fälligkeitsdatum (YYYY-MM-DD):")
    priority = simpledialog.askstring("Aufgabe hinzufügen", "Priorität (hoch/mittel/niedrig):")
    repeat = messagebox.askyesno("Wiederholen", "Soll diese Aufgabe jede Woche wiederholt werden?")
    task = {
        "title": title,
        "description": description or "",
        "due_date": due_date or "",
        "priority": priority or "niedrig",
        "status": "offen",
        "repeat_weekly": repeat
    }
    tasks.append(task)
    selected_task_index = None
    save_tasks()
    refresh_tasks()
    check_notifications()

def edit_task():
    global selected_task_index
    if selected_task_index is None:
        messagebox.showwarning("Bearbeiten", "Keine Aufgabe ausgewählt!")
        return
    task = tasks[selected_task_index]
    task['title'] = simpledialog.askstring("Bearbeiten", "Titel:", initialvalue=task['title']) or task['title']
    task['description'] = simpledialog.askstring("Bearbeiten", "Beschreibung:", initialvalue=task['description']) or task['description']
    task['due_date'] = simpledialog.askstring("Bearbeiten", "Fälligkeitsdatum (YYYY-MM-DD):", initialvalue=task['due_date']) or task['due_date']
    task['priority'] = simpledialog.askstring("Bearbeiten", "Priorität (hoch/mittel/niedrig):", initialvalue=task['priority']) or task['priority']
    task['repeat_weekly'] = messagebox.askyesno("Wiederholen", "Soll diese Aufgabe jede Woche wiederholt werden?")
    selected_task_index = None
    save_tasks()
    refresh_tasks()
    check_notifications()

def delete_task():
    global selected_task_index
    if selected_task_index is None:
        messagebox.showwarning("Löschen", "Keine Aufgabe ausgewählt!")
        return
    confirm = messagebox.askyesno("Löschen", "Wirklich löschen?")
    if confirm:
        tasks.pop(selected_task_index)
        selected_task_index = None
        save_tasks()
        refresh_tasks()

def change_status():
    global selected_task_index
    if selected_task_index is None:
        messagebox.showwarning("Status ändern", "Keine Aufgabe ausgewählt!")
        return
    task = tasks[selected_task_index]
    if task['status'] == "offen":
        task['status'] = "in Arbeit"
    elif task['status'] == "in Arbeit":
        task['status'] = "erledigt"
    else:
        task['status'] = "offen"

    # Wiederholungslogik: wenn erledigt und repeat_weekly = True
    if task['status'] == "erledigt" and task.get("repeat_weekly"):
        try:
            due = datetime.strptime(task["due_date"], "%Y-%m-%d").date()
            new_due = due + timedelta(days=7)
            task["due_date"] = new_due.strftime("%Y-%m-%d")
            task["status"] = "offen"
        except:
            pass

    save_tasks()
    refresh_tasks()

def toggle_theme():
    if ctk.get_appearance_mode() == "Light":
        ctk.set_appearance_mode("Dark")
    else:
        ctk.set_appearance_mode("Light")
    save_tasks()

# -------------------------------
# GUI
# -------------------------------
root = ctk.CTk()
root.title("Termine und Aufgaben")
root.geometry("800x600")
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

main_frame = ctk.CTkFrame(root)
main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_columnconfigure(0, weight=1)

task_frame = ctk.CTkScrollableFrame(main_frame)
task_frame.grid(row=0, column=0, sticky="nsew", pady=(0,10))

button_frame = ctk.CTkFrame(main_frame)
button_frame.grid(row=1, column=0, sticky="ew")
button_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

ctk.CTkButton(button_frame, text="Aufgabe hinzufügen", command=add_task, corner_radius=15).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
ctk.CTkButton(button_frame, text="Bearbeiten", command=edit_task, corner_radius=15).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
ctk.CTkButton(button_frame, text="Löschen", command=delete_task, corner_radius=15).grid(row=0, column=2, padx=5, pady=5, sticky="ew")
ctk.CTkButton(button_frame, text="Status ändern", command=change_status, corner_radius=15).grid(row=0, column=3, padx=5, pady=5, sticky="ew")
ctk.CTkButton(button_frame, text="Light/Dark Mode", command=toggle_theme, corner_radius=15).grid(row=0, column=4, padx=5, pady=5, sticky="ew")

refresh_tasks()
check_notifications()  # Benachrichtigungen beim Start
root.mainloop()
