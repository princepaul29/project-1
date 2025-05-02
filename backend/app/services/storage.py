import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime

class StorageManager:
    def __init__(self, output_dir="data", filename="storage1.json"):
        self.output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
        self.filename = filename
        os.makedirs(self.output_dir, exist_ok=True)
        self.file_path = os.path.join(self.output_dir, self.filename)

    def _load_existing_entries(self):
        if not os.path.exists(self.file_path):
            return []
        
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _prepare_entry(self, item, query=None, source=None):
        if is_dataclass(item):
            item = asdict(item)

        if "timestamp" not in item:
            item["timestamp"] = datetime.now().isoformat()

        item["query"] = query
        item["source"] = source
        return item

    def save_products(self, entries, query=None, source=None):
        if not entries:
            return

        existing = self._load_existing_entries()
        prepared = [self._prepare_entry(e, query=query, source=source) for e in entries]
        updated = existing + prepared

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(updated, f, indent=2)

        print(f"[INFO] Appended {len(prepared)} entries to {self.file_path}")