import json
import os
from datetime import datetime
from django.conf import settings

class FileStorage:
    """Simple file-based storage for non-critical data."""
    
    def __init__(self):
        self.storage_dir = os.path.join(settings.BASE_DIR, 'data_storage')
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def save_generation_log(self, user_id, prompt, image_path):
        """Save image generation log to file."""
        log_file = os.path.join(self.storage_dir, 'generation_log.json')
        
        # Load existing data
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        # Add new entry
        entry = {
            'user_id': str(user_id),
            'prompt': prompt,
            'image_path': image_path,
            'timestamp': datetime.now().isoformat()
        }
        data.append(entry)
        
        # Save back to file
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_user_generations(self, user_id):
        """Get all generations for a user."""
        log_file = os.path.join(self.storage_dir, 'generation_log.json')
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, 'r') as f:
            data = json.load(f)
        
        return [entry for entry in data if entry['user_id'] == str(user_id)]
    
    def save_user_preferences(self, user_id, preferences):
        """Save user preferences to file."""
        prefs_file = os.path.join(self.storage_dir, f'user_{user_id}_prefs.json')
        
        with open(prefs_file, 'w') as f:
            json.dump(preferences, f, indent=2)
    
    def get_user_preferences(self, user_id):
        """Get user preferences from file."""
        prefs_file = os.path.join(self.storage_dir, f'user_{user_id}_prefs.json')
        
        if not os.path.exists(prefs_file):
            return {}
        
        with open(prefs_file, 'r') as f:
            return json.load(f)

# Global instance
file_storage = FileStorage()
