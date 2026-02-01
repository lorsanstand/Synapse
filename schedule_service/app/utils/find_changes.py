from typing import List, Any, Optional
import json

from app.schemas.find_changes import Change

class FindChanges:
    @classmethod
    def find_changes(cls, old_val: Any, new_val: Any, field_name: str = "") -> List[Change]:
        changes = []

        if old_val == new_val:
            return changes

        if isinstance(old_val, dict) and isinstance(new_val, dict):
            all_keys = set(old_val.keys()) | set(new_val.keys())
            for key in all_keys:
                changes.extend(
                    cls.find_changes(old_val.get(key), new_val.get(key), str(key))
                )

        elif isinstance(old_val, list) and isinstance(new_val, list):
            for i in range(max(len(old_val), len(new_val))):
                v_old = old_val[i] if i < len(old_val) else None
                v_new = new_val[i] if i < len(new_val) else None
                changes.extend(cls.find_changes(v_old, v_new, f"item[{i}]"))

        else:
            changes.append(Change(
                field=field_name,
                old=cls._format_val(old_val),
                new=cls._format_val(new_val)
            ))

        return changes

    @staticmethod
    def _format_val(val: Any) -> Optional[str]:
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)