import os
import sys
from PySide6.QtCore import QThread, Signal
import subprocess


class CygateThread(QThread):
    finished = Signal()
    
    def run(self):
        jar_name = resource_path("CyGate_v1.02.jar")
        result = subprocess.run(["java", "-jar", jar_name, "--c", "cygate.txt"])
        self.finished.emit()
        self.quit()
        
        
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)