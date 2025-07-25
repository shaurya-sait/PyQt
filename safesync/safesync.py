# SafeSync
# A PyQt5 application to manage folder backups to AWS S3, scheduling via Windows Task Scheduler

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QComboBox, QListWidget,
    QMessageBox, QGroupBox, QFormLayout, QGridLayout
)
import sys, os, subprocess
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path 

# Load environment variables from .env in the script's directory
dotenv_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=dotenv_path)

class SafeSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafeSync - Backup Tool & Scheduler")
        self.resize(900, 700)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        folder_group = QGroupBox("📂 Folders to Back Up")
        folder_layout = QVBoxLayout()
        self.folder_list = QListWidget()
        browse_btn = QPushButton("Browse Folder")
        remove_folder_btn = QPushButton("Remove Selected")
        browse_btn.clicked.connect(self.browse_folder)
        remove_folder_btn.clicked.connect(self.remove_selected_folder)
        folder_btns = QHBoxLayout()
        folder_btns.addWidget(browse_btn)
        folder_btns.addWidget(remove_folder_btn)
        folder_layout.addWidget(self.folder_list)
        folder_layout.addLayout(folder_btns)
        folder_group.setLayout(folder_layout)

        dest_group = QGroupBox("☁️ Destination & Options")
        dest_layout = QFormLayout()
        self.bucket_input = QLineEdit()
        self.log_input = QLineEdit()
        log_browse_btn = QPushButton("Browse Log File")
        log_browse_btn.clicked.connect(self.browse_log)
        log_row = QHBoxLayout()
        log_row.addWidget(self.log_input)
        log_row.addWidget(log_browse_btn)
        self.glacier_checkbox = QCheckBox("Use Glacier Instant Retrieval")
        dest_layout.addRow("S3 Bucket:", self.bucket_input)
        dest_layout.addRow("Log File:", log_row)
        dest_layout.addRow("", self.glacier_checkbox)

        # AWS Credentials (Debug Only)
        self.aws_access_input = QLineEdit()
        self.aws_secret_input = QLineEdit()
        self.aws_secret_input.setEchoMode(QLineEdit.Password)
        dest_layout.addRow("AWS Access Key ID:", self.aws_access_input)
        dest_layout.addRow("AWS Secret Access Key:", self.aws_secret_input)

        dest_group.setLayout(dest_layout)

        sched_group = QGroupBox("⏰ Schedule Settings")
        sched_layout = QGridLayout()
        self.hour_dropdown = QComboBox()
        self.minute_dropdown = QComboBox()
        self.hour_dropdown.addItems([f"{i:02d}" for i in range(24)])
        self.minute_dropdown.addItems(["00", "15", "30", "45"])
        sched_layout.addWidget(QLabel("Time:"), 0, 0)
        sched_layout.addWidget(self.hour_dropdown, 0, 1)
        sched_layout.addWidget(QLabel(":"), 0, 2)
        sched_layout.addWidget(self.minute_dropdown, 0, 3)
        self.day_checkboxes = {}
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for idx, day in enumerate(days):
            cb = QCheckBox(day)
            self.day_checkboxes[day.upper()] = cb
            sched_layout.addWidget(cb, 1 + idx // 4, idx % 4)
        sched_group.setLayout(sched_layout)

        script_group = QGroupBox("📜 Script Actions")
        script_layout = QVBoxLayout()
        self.script_selector = QComboBox()
        self.preview = QTextEdit()
        gen_btn = QPushButton("Generate Script")
        run_btn = QPushButton("Run Now")
        sched_btn = QPushButton("Schedule")
        del_script_btn = QPushButton("Delete Script")
        gen_btn.clicked.connect(self.generate_script)
        run_btn.clicked.connect(self.run_backup_now)
        sched_btn.clicked.connect(self.schedule_backup)
        del_script_btn.clicked.connect(self.delete_selected_script)
        script_btns = QHBoxLayout()
        script_btns.addWidget(gen_btn)
        script_btns.addWidget(run_btn)
        script_btns.addWidget(sched_btn)
        script_btns.addWidget(del_script_btn)
        script_layout.addWidget(QLabel("Saved Scripts:"))
        script_layout.addWidget(self.script_selector)
        script_layout.addLayout(script_btns)
        script_layout.addWidget(QLabel("Script Preview:"))
        script_layout.addWidget(self.preview)
        script_group.setLayout(script_layout)

        task_group = QGroupBox("📂 Scheduled Tasks")
        task_layout = QHBoxLayout()
        self.task_selector = QComboBox()
        delete_task_btn = QPushButton("Delete Task")
        delete_task_btn.clicked.connect(self.remove_selected_task)
        task_layout.addWidget(self.task_selector)
        task_layout.addWidget(delete_task_btn)
        task_group.setLayout(task_layout)

        tools_group = QGroupBox("🛠️ System & AWS Tools")
        tools_layout = QHBoxLayout()
        test_btn = QPushButton("Test AWS Credentials")
        help_btn = QPushButton("AWS Setup Help")
        reload_btn = QPushButton("🔄 Reload .env")
        test_btn.clicked.connect(self.test_aws_credentials)
        help_btn.clicked.connect(self.show_aws_help)
        reload_btn.clicked.connect(self.load_env_into_fields)
        tools_layout.addWidget(test_btn)
        tools_layout.addWidget(help_btn)
        tools_layout.addWidget(reload_btn)
        tools_group.setLayout(tools_layout)

        layout.addWidget(folder_group)
        layout.addWidget(dest_group)
        layout.addWidget(sched_group)
        layout.addWidget(script_group)
        layout.addWidget(task_group)
        layout.addWidget(tools_group)
        self.setLayout(layout)

        self.update_script_list()
        self.update_task_list()
        self.load_env_into_fields()  # Load environment values after UI is ready

    def load_env_into_fields(self):
        dotenv_path = Path(__file__).resolve().parent / ".env"

    # Clear previous values from environment memory
        for key in ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "BUCKET_NAME"]:
            os.environ.pop(key, None)

    # Load from file only if it exists
        if dotenv_path.exists():
            load_dotenv(dotenv_path=dotenv_path, override=True)

        self.bucket_input.setText(os.getenv("BUCKET_NAME", ""))
        self.aws_access_input.setText(os.getenv("AWS_ACCESS_KEY_ID", ""))
        self.aws_secret_input.setText(os.getenv("AWS_SECRET_ACCESS_KEY", ""))


    def browse_folder(self):
        """
        Open directory picker and add to folder_list
        """
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_list.addItem(folder)

    def remove_selected_folder(self):
        """
        Remove selected entries from folder_list
        """
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def browse_log(self):
        """
        Open save-file dialog to choose log file path
        """
        path, _ = QFileDialog.getSaveFileName(self, "Select Log File", "", "Text Files (*.txt)")
        if path:
            self.log_input.setText(path)

    def generate_script(self):
        """
        Compose AWS CLI commands and save as .bat file
        """
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        bucket = self.bucket_input.text().strip()
        log = self.log_input.text().strip()
        glacier = self.glacier_checkbox.isChecked()

        # Validate inputs
        if not folders or not bucket:
            QMessageBox.critical(self, "Error", "Folders and bucket name are required.")
            return
        
        # Build command lines
        lines = ["@echo off"]
        for folder in folders:
            name = os.path.basename(folder)
            cmd = f'aws s3 sync "{folder}" "s3://{bucket}/{name}/" --exact-timestamps'
            if glacier:
                cmd += ' --storage-class GLACIER_IR'
            lines.append(cmd)
        if log:
            lines.append(f'echo Backup completed at %DATE% %TIME% >> "{log}"')
        script_content = "\n".join(lines)
        self.preview.setPlainText(script_content)  # Show preview

        # Save to disk with timestamped filename
        base_dir = r"C:\safesync"
        script_dir = os.path.join(base_dir, "scripts")
        os.makedirs(script_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.bat"
        path = os.path.join(script_dir, filename)
        with open(path, "w") as f:
            f.write(script_content)
        QMessageBox.information(self, "Saved", f"Script saved to: {path}")
        self.update_script_list()

    def run_backup_now(self):
        """
        Execute the selected .bat script immediately
        """
        script = self.script_selector.currentData()
        if not script:
            QMessageBox.warning(self, "No Script", "Please select a script.")
            return
        path = os.path.join(r"C:\safesync", "scripts", script)
        try:
            subprocess.run(["cmd", "/c", path], check=True)
            QMessageBox.information(self, "Backup", "Backup ran successfully.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Backup failed:\n{e}")

    def schedule_backup(self):
        """
        Create or update a Windows scheduled task for the selected script
        """
        script = self.script_selector.currentData()
        if not script:
            QMessageBox.warning(self, "No Script", "Please select a script.")
            return
        days = [d for d, cb in self.day_checkboxes.items() if cb.isChecked()]
        if not days:
            QMessageBox.warning(self, "No Days", "Select at least one day.")
            return
        time_str = f"{self.hour_dropdown.currentText()}:{self.minute_dropdown.currentText()}"
        task_name = f"AutoS3Backup_{os.path.splitext(script)[0]}"
        cmd_base = ["schtasks", "/create", "/tn", task_name, "/tr", os.path.join(r"C:\safesync", "scripts", script)]
        if set(days) == set(["MON","TUE","WED","THU","FRI","SAT","SUN"]):
            cmd = cmd_base + ["/sc", "daily", "/st", time_str]
        else:
            cmd = cmd_base + ["/sc", "weekly", "/d", ",".join(days), "/st", time_str]
        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Scheduled", f"Scheduled on {','.join(days)} at {time_str}")
            self.update_task_list()
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", "Failed to schedule task.")

    def delete_selected_script(self):
        """
        Delete the selected .bat script from disk
        """
        script = self.script_selector.currentData()
        if not script:
            QMessageBox.warning(self, "No Script", "Please select a script.")
            return
        path = os.path.join(r"C:\safesync", "scripts", script)
        try:
            os.remove(path)
            QMessageBox.information(self, "Deleted", f"Deleted {script}")
            self.update_script_list()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Delete failed:\n{e}")

    def remove_selected_task(self):
        """
        Remove the selected scheduled task
        """
        task = self.task_selector.currentData()
        if not task:
            QMessageBox.warning(self, "No Task", "Please select a task.")
            return
        try:
            subprocess.run(["schtasks", "/delete", "/tn", task, "/f"], check=True)
            QMessageBox.information(self, "Removed", f"Task '{task}' deleted.")
            self.update_task_list()
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", "Failed to delete task.")

    def update_task_list(self):
        """
        Populate the scheduled tasks dropdown with name and next-run timestamp.
        """
        self.task_selector.clear()
        try:
            out = subprocess.run(
                "schtasks /query /fo LIST /v", shell=True, text=True, capture_output=True
            ).stdout
            lines = out.splitlines()
            entries = []
            i = 0
            while i < len(lines):
                if lines[i].startswith("TaskName:"):
                    raw_name = lines[i].split(":",1)[1].strip().lstrip("\\")
                    next_run = ""
                    j = i + 1
                    while j < len(lines) and not lines[j].startswith("TaskName:"):
                        if lines[j].startswith("Next Run Time:"):
                            next_run = lines[j].split(":",1)[1].strip()
                            break
                        j += 1
                    if raw_name.lower().startswith("autos3backup_"):
                        display = f"{raw_name} (Next: {next_run})"
                        entries.append((display, raw_name))
                    i = j
                else:
                    i += 1
            for disp, raw in entries:
                self.task_selector.addItem(disp, raw)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not list tasks:\n{e}")

    def update_script_list(self):
        """
        Populate script dropdown with filename and last-modified timestamp.
        """
        self.script_selector.clear()
        script_dir = r"C:\safesync\scripts"
        if os.path.isdir(script_dir):
            for fname in sorted(os.listdir(script_dir)):
                if fname.endswith(".bat"):
                    full = os.path.join(script_dir, fname)
                    mtime = datetime.fromtimestamp(os.path.getmtime(full))
                    # Format timestamp for display
                    ts = mtime.strftime("%Y-%m-%d %H:%M:%S")
                    display = f"{fname} ({ts})"
                    self.script_selector.addItem(display, fname)

    def test_aws_credentials(self):
        """
        Verify AWS credentials via sts get-caller-identity.
        """
        try:
            res = subprocess.run("aws sts get-caller-identity", shell=True, text=True, capture_output=True)
            if res.returncode == 0:
                QMessageBox.information(self, "AWS Credentials", "✅ AWS credentials are valid.")
            else:
                QMessageBox.critical(self, "AWS Credentials", f"❌ Failed:\n{res.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception: {e}")

    def show_aws_help(self):
        """
        Display basic AWS CLI setup instructions.
        """
        QMessageBox.information(self, "AWS Setup Help",
            "1. Install AWS CLI\n2. aws configure\n3. Test with sts get-caller-identity")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SafeSyncApp()
    win.show()
    sys.exit(app.exec())
