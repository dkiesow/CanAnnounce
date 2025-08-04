import requests
import os
import datetime

def upload_file_to_course(token, base_url, course_id, file_path):
    """
    Upload a file to a Canvas course and return the file download URL.
    """
    headers = {
        'Authorization': f'Bearer {token}'
    }
    filename = os.path.basename(file_path)
    # Step 1: Start the file upload
    url = f"{base_url}/api/v1/courses/{course_id}/files"
    params = {
        'name': filename,
        'parent_folder_path': '/uploaded_announcements',
        'overwrite': True
    }
    with open(file_path, 'rb') as f:
        # Step 2: Get upload URL and params
        init_resp = requests.post(url, headers=headers, data=params)
        if init_resp.status_code != 200:
            print(f"Failed to initiate file upload: {init_resp.text}")
            return None
        upload_info = init_resp.json()
        upload_url = upload_info['upload_url']
        upload_params = upload_info['upload_params']
        # Step 3: Upload the file
        files = {'file': (filename, f)}
        upload_resp = requests.post(upload_url, data=upload_params, files=files)
        if upload_resp.status_code not in (200, 201, 302):
            print(f"Failed to upload file: {upload_resp.text}")
            return None
        # Step 4: Get file download URL
        if upload_resp.status_code == 302:
            # Some Canvas instances redirect after upload
            location = upload_resp.headers['Location']
            file_info = requests.get(location, headers=headers).json()
        else:
            file_info = upload_resp.json()
        return file_info.get('url')

def create_announcement_with_file(token, base_url, course_id, course_name):
    import importlib.util
    import sys
    # Dynamically import config.py
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    spec = importlib.util.spec_from_file_location('config', config_path)
    config = importlib.util.module_from_spec(spec)
    sys.modules['config'] = config
    spec.loader.exec_module(config)
    publish_status = getattr(config, 'ANNOUNCEMENT_PUBLISH', False)

    print(f"\n--- Announcement Creation ---")
    print(f"Course: {course_name} (ID: {course_id})")
    print(f"Announcement will be published immediately: {publish_status}")
    if not publish_status:
        print("(It will be scheduled to post 30 days in the future)")

    file_path = input("Enter the path to the file to upload: ").strip()
    if not file_path:
        print("No file path provided. Aborting announcement creation.")
        return
    file_path = file_path.strip()
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}\nPlease check the path and try again.")
        return
    file_url = upload_file_to_course(token, base_url, course_id, file_path)
    if not file_url:
        print("File upload failed. Cannot create announcement.")
        return
    title = input("Enter the announcement title: ")
    print("Enter the announcement body (HTML supported, blank line to finish each paragraph):")
    paragraphs = []
    while True:
        para = input()
        if para == '':
            break
        paragraphs.append(para)
    # Compose the announcement body with the file link at the top using HTML
    announcement_body = f'<a href="{file_url}">Today\'s slides are here</a> <p></p>'
    for para in paragraphs:
        announcement_body += f'{para}<p></p>'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics"
    payload = {
        'title': title,
        'message': announcement_body,
        'is_announcement': True
    }
    if not publish_status:
        # Schedule for 30 days in the future
        future_date = (datetime.datetime.utcnow() + datetime.timedelta(days=30)).isoformat() + 'Z'
        payload['delayed_post_at'] = future_date
    resp = requests.post(url, headers=headers, data=payload)
    if resp.status_code in (200, 201):
        print("Announcement posted successfully!")
    else:
        print(f"Failed to post announcement: {resp.text}")

def create_announcement_with_file_gui(token, base_url, course_id, course_name):
    import importlib.util
    import sys
    import datetime
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    from tkinter import simpledialog
    from tkinter import ttk
    import os

    # Dynamically import config.py
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    spec = importlib.util.spec_from_file_location('config', config_path)
    config = importlib.util.module_from_spec(spec)
    sys.modules['config'] = config
    spec.loader.exec_module(config)
    publish_status = getattr(config, 'ANNOUNCEMENT_PUBLISH', False)

    # Calculate default title
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')
    month_day_year = now.strftime('%-m/%-d/%y') if hasattr(now, 'strftime') else now.strftime('%m/%d/%y')
    # Trim course name: remove up to and including first hyphen, and remove from last hyphen to end
    trimmed_course_name = course_name
    if '-' in trimmed_course_name:
        # Remove up to and including first hyphen
        trimmed_course_name = trimmed_course_name.split('-', 1)[-1].strip()
    if '-' in trimmed_course_name:
        # Remove from last hyphen to end
        trimmed_course_name = trimmed_course_name.rsplit('-', 1)[0].strip()
    default_title = f"{trimmed_course_name} - Today's Slides - {day_of_week} {month_day_year}"
    default_body = f'<a href="[FILE_URL_PLACEHOLDER]">Today\'s slides are here</a>\n\nENTER BODY TEXT\n\n'

    # Fetch upcoming assignments for the course
    from course_utils import get_upcoming_assignments
    upcoming_assignments = get_upcoming_assignments(token, base_url, course_id)

    # Format upcoming assignments for display without HTML tags
    if upcoming_assignments:
        assignments_text = '\n'.join(
            [f"- {assignment['name']} (Due: {assignment['due_at']})" for assignment in upcoming_assignments]
        )
        default_body += f"Upcoming Assignments:\n{assignments_text}"
    else:
        default_body += "No upcoming assignments at this time."

    class AnnouncementApp(tk.Tk):
        def __init__(self):
            super().__init__()
            self.title('Create Canvas Announcement')
            self.geometry('700x600')
            self.file_path = ''
            self.file_url = ''
            self.create_widgets()

        def create_widgets(self):
            tk.Label(self, text=f"Course: {course_name} (ID: {course_id})", font=('Arial', 12, 'bold')).pack(pady=(5, 0))
            tk.Label(self, text=f"Announcement will be published immediately: {publish_status}", fg='blue').pack(pady=(0, 5))
            if not publish_status:
                tk.Label(self, text="(It will be scheduled to post 30 days in the future)", fg='orange').pack()

            # File selection
            file_frame = tk.Frame(self)
            file_frame.pack(pady=5)
            tk.Label(file_frame, text="File to upload:").pack(side=tk.LEFT)
            self.file_entry = tk.Entry(file_frame, width=50)
            self.file_entry.pack(side=tk.LEFT, padx=5)
            tk.Button(file_frame, text="Browse", command=self.browse_file).pack(side=tk.LEFT)

            # Title
            tk.Label(self, text="Announcement Title:").pack(pady=(10,0))
            self.title_entry = tk.Entry(self, width=80, justify='left')
            self.title_entry.pack(pady=2)
            self.title_entry.insert(0, default_title)

            # Body
            tk.Label(self, text="Announcement Body (HTML, one paragraph per line):").pack(pady=(10,0))
            self.body_text = scrolledtext.ScrolledText(self, width=80, height=12)
            self.body_text.pack(pady=2)
            self.body_text.insert('1.0', default_body)

            # Preview
            tk.Button(self, text="Preview", command=self.preview_announcement).pack(pady=5)
            self.preview_label = tk.Label(self, text="", justify=tk.LEFT, anchor='w', wraplength=650, bg='white', relief='sunken')
            self.preview_label.pack(fill=tk.BOTH, expand=False, padx=10, pady=5)

            # Submit
            tk.Button(self, text="Submit Announcement", command=self.submit_announcement).pack(pady=10)

        def browse_file(self):
            path = filedialog.askopenfilename()
            if path:
                self.file_entry.delete(0, tk.END)
                self.file_entry.insert(0, path)
                self.file_path = path
                # Do not overwrite the body text here; let user edit freely

        def preview_announcement(self):
            file_url = self.file_entry.get().strip()
            if not file_url:
                file_url = '[No file selected]'
            else:
                file_url = os.path.basename(file_url)
            paragraphs = self.body_text.get('1.0', tk.END).strip().split('\n')
            html = f'<a href="#">Today\'s slides are here</a> <p></p>'
            for para in paragraphs:
                if para.strip():
                    html += f'{para}<p></p>'
            preview_html = f"<b>Preview:</b>\n{html}"
            self.preview_label.config(text=preview_html)

        def submit_announcement(self):
            import requests
            from datetime import datetime, timedelta
            from config import UPCOMING_ASSIGNMENT_DAYS
            file_path = self.file_entry.get().strip()
            if not file_path or not os.path.isfile(file_path):
                messagebox.showerror("Error", "File not found. Please select a valid file.")
                return
            file_url = upload_file_to_course(token, base_url, course_id, file_path)
            if not file_url:
                messagebox.showerror("Error", "File upload failed. Cannot create announcement.")
                return
            title = self.title_entry.get().strip()
            if not title:
                messagebox.showerror("Error", "Please enter a title.")
                return
            body_content = self.body_text.get('1.0', tk.END).strip()

            # Check for placeholder text
            if "ENTER BODY TEXT" in body_content:
                messagebox.showerror("Error", "Please replace the placeholder text before submitting.")
                return

            # Replace the placeholder with the actual Canvas file URL
            announcement_body = body_content.replace('[FILE_URL_PLACEHOLDER]', file_url)

            # Fetch assignments due in the next configurable number of days
            try:
                assignments = get_course_assignments(token, base_url, course_id)
                now = datetime.utcnow()
                lookahead = now + timedelta(days=UPCOMING_ASSIGNMENT_DAYS)
                upcoming = []
                for a in assignments:
                    due = a.get('due_at')
                    if due:
                        try:
                            due_dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
                            if now <= due_dt <= lookahead:
                                name = a.get('name', 'Unnamed Assignment')
                                due_str = due_dt.strftime('%a %m/%d %H:%M')
                                upcoming.append(f'<li>{name} (Due: {due_str})</li>')
                        except Exception:
                            continue
                if upcoming:
                    announcement_body += '<br><b>Upcoming assignments</b><br><ol>' + ''.join(upcoming) + '</ol>'
            except Exception as e:
                # If assignment fetch fails, just skip
                pass

            headers = {
                'Authorization': f'Bearer {token}'
            }
            url = f"{base_url}/api/v1/courses/{course_id}/discussion_topics"
            payload = {
                'title': title,
                'message': announcement_body,
                'is_announcement': True
            }
            if not publish_status:
                # Fix timezone-aware datetime
                from datetime import datetime, timezone, timedelta

                # Update the future_date calculation
                future_date = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
                payload['delayed_post_at'] = future_date
            resp = requests.post(url, headers=headers, data=payload)
            if resp.status_code in (200, 201):
                messagebox.showinfo("Success", "Announcement posted successfully!")
                self.destroy()
            else:
                messagebox.showerror("Error", f"Failed to post announcement: {resp.text}")

    app = AnnouncementApp()
    app.mainloop()

def calculate_trimmed_title(course_name):
    """
    Generate a trimmed course title with the format:
    "<Trimmed Course Name> Slides from <Day of Week> <Date>"
    """
    # Get the current date
    now = datetime.datetime.now()
    day_of_week = now.strftime('%A')
    month_day_year = now.strftime('%m/%d')  # Ensure consistent MM/DD format

    # Trim course name: remove up to and including first hyphen, and remove from last hyphen to end
    trimmed_course_name = course_name
    if '-' in trimmed_course_name:
        # Remove up to and including first hyphen
        trimmed_course_name = trimmed_course_name.split('-', 1)[-1].strip()
    if '-' in trimmed_course_name:
        # Remove from last hyphen to end
        trimmed_course_name = trimmed_course_name.rsplit('-', 1)[0].strip()

    # Format the title
    return f"{trimmed_course_name} Slides from {day_of_week} {month_day_year}"
