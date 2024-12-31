import os
import subprocess
import sys
from PyQt5 import QtWidgets, QtGui, QtCore

class TorTrafficRouterApp(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Tor Traffic Router")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #552583;")  # Tor's signature purple color

        # Header Label
        self.header_label = QtWidgets.QLabel("Dimensional Rift - Tor Traffic Router", self)
        self.header_label.setGeometry(20, 10, 760, 50)
        self.header_label.setAlignment(QtCore.Qt.AlignCenter)
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        # Status Label
        self.status_label = QtWidgets.QLabel("Status: Disconnected", self)
        self.status_label.setGeometry(20, 70, 760, 30)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; color: red;")

        # Log Viewer
        self.log_viewer = QtWidgets.QTextEdit(self)
        self.log_viewer.setGeometry(20, 120, 760, 300)
        self.log_viewer.setReadOnly(True)
        self.log_viewer.setStyleSheet("background-color: #f9f9f9; border: 1px solid #ccc; color: #333;")
        self.log_viewer.setPlaceholderText("Logs will appear here...")

        # Control Buttons
        self.start_button = QtWidgets.QPushButton("Start Tor Routing", self)
        self.start_button.setGeometry(50, 450, 200, 50)
        self.start_button.setStyleSheet("font-size: 16px; background-color: #6a1b9a; color: white; border-radius: 5px;")
        self.start_button.clicked.connect(self.start_tor_routing)

        self.stop_button = QtWidgets.QPushButton("Stop Tor Routing", self)
        self.stop_button.setGeometry(300, 450, 200, 50)
        self.stop_button.setStyleSheet("font-size: 16px; background-color: #6a1b9a; color: white; border-radius: 5px;")
        self.stop_button.clicked.connect(self.stop_tor_routing)
        self.stop_button.setEnabled(False)

        self.new_identity_button = QtWidgets.QPushButton("New Tor Identity", self)
        self.new_identity_button.setGeometry(550, 450, 200, 50)
        self.new_identity_button.setStyleSheet("font-size: 16px; background-color: #6a1b9a; color: white; border-radius: 5px;")
        self.new_identity_button.clicked.connect(self.new_tor_identity)
        self.new_identity_button.setEnabled(False)

        # Export Logs Button
        self.export_logs_button = QtWidgets.QPushButton("Export Logs", self)
        self.export_logs_button.setGeometry(300, 520, 200, 50)
        self.export_logs_button.setStyleSheet("font-size: 16px; background-color: #4a148c; color: white; border-radius: 5px;")
        self.export_logs_button.clicked.connect(self.export_logs)

    def log_message(self, message):
        self.log_viewer.append(message)

    def export_logs(self):
        try:
            with open("tor_router_logs.txt", "w") as log_file:
                log_file.write(self.log_viewer.toPlainText())
            QtWidgets.QMessageBox.information(self, "Success", "Logs exported to tor_router_logs.txt")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to export logs: {e}")

    def start_tor_routing(self):
        try:
            self.check_dependencies()
            self.start_tor_linux()

            self.status_label.setText("Status: Connected")
            self.status_label.setStyleSheet("font-size: 18px; color: green;")
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.new_identity_button.setEnabled(True)
        except Exception as e:
            self.log_message(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to start Tor routing: {e}")

    def stop_tor_routing(self):
        try:
            self.stop_tor_linux()

            self.status_label.setText("Status: Disconnected")
            self.status_label.setStyleSheet("font-size: 18px; color: red;")
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.new_identity_button.setEnabled(False)
        except Exception as e:
            self.log_message(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to stop Tor routing: {e}")

    def new_tor_identity(self):
        try:
            subprocess.run(["sudo", "killall", "-HUP", "tor"], check=True)
            self.log_message("New Tor identity requested successfully.")
        except subprocess.CalledProcessError as e:
            self.log_message(f"Error: {e}")
            QtWidgets.QMessageBox.critical(self, "Error", f"Failed to request new Tor identity: {e}")

    def check_dependencies(self):
        self.log_message("Checking Linux dependencies...")
        required_cmds = ["tor", "iptables"]
        for cmd in required_cmds:
            if subprocess.run(["which", cmd], stdout=subprocess.DEVNULL).returncode != 0:
                raise EnvironmentError(f"{cmd} is not installed. Please install it first.")

    def start_tor_linux(self):
        self.log_message("Starting Tor service on Linux...")
        subprocess.run(["sudo", "systemctl", "start", "tor"], check=True)

        self.log_message("Configuring iptables rules for Tor routing...")
        subprocess.run(["sudo", "iptables", "-F"], check=True)
        subprocess.run(["sudo", "iptables", "-t", "nat", "-F"], check=True)
        subprocess.run(["sudo", "iptables", "-t", "nat", "-A", "OUTPUT", "-m", "owner", "!", "--uid-owner", "debian-tor", "-j", "REDIRECT", "--to-ports", "9040"], check=True)
        subprocess.run(["sudo", "iptables", "-A", "OUTPUT", "-m", "owner", "!", "--uid-owner", "debian-tor", "-j", "ACCEPT"], check=True)

        self.log_message("Updating DNS settings...")
        with open("/etc/resolv.conf", "w") as resolv_conf:
            resolv_conf.write("nameserver 127.0.0.1\n")

    def stop_tor_linux(self):
        self.log_message("Stopping Tor service on Linux...")
        subprocess.run(["sudo", "systemctl", "stop", "tor"], check=True)

        self.log_message("Clearing iptables rules...")
        subprocess.run(["sudo", "iptables", "-F"], check=True)
        subprocess.run(["sudo", "iptables", "-t", "nat", "-F"], check=True)

        self.log_message("Restoring DNS settings...")
        with open("/etc/resolv.conf", "w") as resolv_conf:
            resolv_conf.write("nameserver 8.8.8.8\n")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = TorTrafficRouterApp()
    window.show()
    sys.exit(app.exec_())