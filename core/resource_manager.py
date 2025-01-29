import os
import sys
import json

class ResourceManager:
    @staticmethod
    def get_base_path():
        """Get the base path for resources whether running as script or exe"""
        if getattr(sys, 'frozen', False):
            # Running as compiled exe
            return sys._MEIPASS
        else:
            # Running as script
            return os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

    @staticmethod
    def get_resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        base_path = ResourceManager.get_base_path()
        return os.path.join(base_path, relative_path)

    @staticmethod
    def load_json_resource(relative_path):
        """Load JSON file from resources"""
        try:
            with open(ResourceManager.get_resource_path(relative_path), 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading resource {relative_path}: {e}")
            return None 