# SafeSync
# Import Required PyQt5 Modules
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit,
    QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QComboBox, QListWidget, QMessageBox
)
import sys, os, subprocess
from datetime import datetime

class SafeSyncApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafeSync - Backup Tool")
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        # --- folder selection ---
        browse_folder = QPushButton("Browse for Folder")
        browse_folder.clicked.connect(self.browse_folder)
        self.folder_list = QListWidget()
        remove_folder = QPushButton("Remove Selected Folder")
        remove_folder.clicked.connect(self.remove_selected_folder)

        # --- bucket & log ---
        self.bucket_input = QLineEdit()
        self.log_input = QLineEdit()
        browse_log = QPushButton("Browse")
        browse_log.clicked.connect(self.browse_log)

        # --- glacier toggle ---
        self.glacier_checkbox = QCheckBox("🧊 Use Glacier Instant Retrieval")

        # --- time pickers ---
        self.hour_dropdown = QComboBox()
        self.hour_dropdown.addItems([f"{i:02d}" for i in range(24)])
        self.minute_dropdown = QComboBox()
        self.minute_dropdown.addItems(["00", "15", "30", "45"])

        # --- script preview & controls ---
        self.preview = QTextEdit()
        generate_button = QPushButton("🚀 Generate Script")
        generate_button.clicked.connect(self.generate_script)
        run_button = QPushButton("🕒 Run Backup Now")
        run_button.clicked.connect(self.run_backup_now)
        schedule_button = QPushButton("📅 Schedule Backup")
        schedule_button.clicked.connect(self.schedule_backup)

        # --- AWS test & help ---
        test_aws_button = QPushButton("🔑 Test AWS Credentials")
        test_aws_button.clicked.connect(self.test_aws_credentials)
        aws_help_button = QPushButton("🧰 AWS Setup Help")
        aws_help_button.clicked.connect(self.show_aws_help)

        # --- task selector & delete ---
        self.task_selector = QComboBox()
        remove_task_button = QPushButton("❌ Delete Selected Task")
        remove_task_button.clicked.connect(self.remove_selected_task)

        # --- glacier info ---
        glacier_info_button = QPushButton("❓ Glacier Info")
        glacier_info_button.clicked.connect(self.show_glacier_info)

        # --- layout ---
        layout = QVBoxLayout()
        layout.addWidget(QLabel("📂 Folder(s) to Back Up"))
        layout.addWidget(browse_folder)
        layout.addWidget(self.folder_list)
        layout.addWidget(remove_folder)

        layout.addWidget(QLabel("☁️ S3 Bucket Name"))
        layout.addWidget(self.bucket_input)

        layout.addWidget(QLabel("📝 Log File Path"))
        layout.addWidget(self.log_input)
        layout.addWidget(browse_log)

        layout.addWidget(self.glacier_checkbox)

        layout.addWidget(QLabel("⏰ Time"))
        tlay = QHBoxLayout()
        tlay.addWidget(self.hour_dropdown)
        tlay.addWidget(QLabel(":"))
        tlay.addWidget(self.minute_dropdown)
        layout.addLayout(tlay)

        layout.addWidget(generate_button)
        layout.addWidget(run_button)
        layout.addWidget(schedule_button)
        layout.addWidget(test_aws_button)

        layout.addWidget(QLabel("🗂 Select Scheduled Task"))
        layout.addWidget(self.task_selector)
        layout.addWidget(remove_task_button)

        layout.addWidget(QLabel("📄 Preview Script"))
        layout.addWidget(self.preview)

        layout.addWidget(aws_help_button)
        layout.addWidget(glacier_info_button)

        self.setLayout(layout)

        # initial population of existing tasks
        self.update_task_list()

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_list.addItem(folder)

    def remove_selected_folder(self):
        for item in self.folder_list.selectedItems():
            self.folder_list.takeItem(self.folder_list.row(item))

    def browse_log(self):
        path, _ = QFileDialog.getSaveFileName(self, "Select Log File", "", "Text Files (*.txt)")
        if path:
            self.log_input.setText(path)

    def generate_script(self):
        folders = [self.folder_list.item(i).text() for i in range(self.folder_list.count())]
        bucket = self.bucket_input.text().strip()
        log = self.log_input.text().strip()
        glacier = self.glacier_checkbox.isChecked()
        hour = self.hour_dropdown.currentText()
        minute = self.minute_dropdown.currentText()

        if not folders or not bucket:
            QMessageBox.critical(self, "Error", "Folders and bucket name are required.")
            return

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
        self.preview.setPlainText(script_content)

        save_dir = os.path.join(os.path.expanduser("~"), "Documents", "SafeSync")
        os.makedirs(save_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        script_path = os.path.join(save_dir, f"backup_{timestamp}.bat")
        with open(script_path, "w") as f:
            f.write(script_content)
        QMessageBox.information(self, "Saved", f"Backup script saved to:\n{script_path}")

    def schedule_backup(self):
        script, _ = QFileDialog.getOpenFileName(self, "Select Script to Schedule", "", "Batch files (*.bat)")
        if not script:
            return

        hour = self.hour_dropdown.currentText()
        minute = self.minute_dropdown.currentText()
        time_str = f"{hour}:{minute}"
        task_name = f"AutoS3Backup_{os.path.splitext(os.path.basename(script))[0]}"

        # use a list for subprocess to avoid nested-quote issues
        cmd = [
            "schtasks", "/create",
            "/tn", task_name,
            "/tr", script,
            "/sc", "daily",
            "/st", time_str
        ]

        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Scheduled", f"Backup scheduled daily at {time_str}")
            # ← refresh the combo immediately
            self.update_task_list()
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", "Failed to schedule task.")

    def run_backup_now(self):
        script, _ = QFileDialog.getOpenFileName(self, "Select Script to Run", "", "Batch files (*.bat)")
        if not script:
            return
        try:
            subprocess.run(["cmd", "/c", script], check=True)
            QMessageBox.information(self, "Backup", "Backup ran successfully.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Backup failed:\n{e}")

    def remove_selected_task(self):
        display_name = self.task_selector.currentText()
        if not display_name:
            QMessageBox.warning(self, "No Task", "Please select a task to delete.")
            return

        # re-add leading slash so schtasks finds it
        task_name = f"\\{display_name}"
        cmd = ["schtasks", "/delete", "/tn", task_name, "/f"]

        try:
            subprocess.run(cmd, check=True)
            QMessageBox.information(self, "Removed", f"Task '{display_name}' deleted.")
            self.update_task_list()
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Error", f"Failed to delete task '{display_name}'.")

    def test_aws_credentials(self):
        try:
            result = subprocess.run("aws sts get-caller-identity", shell=True, text=True, capture_output=True)
            if result.returncode == 0:
                QMessageBox.information(self, "AWS Credentials", "✅ AWS credentials are valid and CLI is configured.")
            else:
                QMessageBox.critical(self, "AWS Credentials", f"❌ Failed to verify credentials:\n{result.stderr}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Exception during AWS credentials test:\n{e}")

    def update_task_list(self):
        try:
            result = subprocess.run("schtasks /query /fo LIST", shell=True, text=True, capture_output=True)
            task_names = []
            for line in result.stdout.splitlines():
                if line.startswith("TaskName:"):
                    name = line.split(":", 1)[1].strip()
                    if name.lower().startswith("\\autos3backup_"):
                        # strip the leading backslash for display
                        task_names.append(name.lstrip("\\"))
            self.task_selector.clear()
            self.task_selector.addItems(task_names)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not list tasks:\n{e}")

    def show_aws_help(self):
        help_text = (
            "🧰 AWS Setup Help:\n\n"
            "1. Install AWS CLI from https://aws.amazon.com/cli/\n"
            "2. Run `aws configure` in your terminal.\n"
            "3. Enter your AWS Access Key, Secret Key, Region, and output format.\n"
            "4. Use `aws sts get-caller-identity` to test.\n\n"
            "SafeSync uses these credentials to sync files to your S3 bucket."
        )
        QMessageBox.information(self, "AWS Setup Help", help_text)

    def show_glacier_info(self):
        info_text = (
            "❓ Glacier Instant Retrieval Info:\n\n"
            "– Lower cost than Standard.\n"
            "– Millisecond retrieval.\n"
            "– Great for archives and backups."
        )
        QMessageBox.information(self, "Glacier Info", info_text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SafeSyncApp()
    win.show()
    sys.exit(app.exec())
