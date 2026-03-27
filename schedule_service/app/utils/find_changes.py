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
            # Быстрый выход: идентичные списки с учетом порядка элементов как множества
            # (помогает избежать ложных срабатываний при перестановке подгрупп).
            if cls._canonical(old_val) == cls._canonical(new_val):
                return changes

            if cls._is_list_of_dicts(old_val) and cls._is_list_of_dicts(new_val):
                changes.extend(cls._find_changes_in_dict_lists(old_val, new_val, field_name))
            else:
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

    @staticmethod
    def _canonical(val: Any) -> str:
        """Каноническое представление JSON-структуры с игнорированием порядка в списках."""
        def _normalize(value: Any):
            if isinstance(value, dict):
                return {k: _normalize(v) for k, v in sorted(value.items(), key=lambda x: x[0])}
            if isinstance(value, list):
                normalized_items = [_normalize(item) for item in value]
                return sorted(normalized_items, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True))
            return value

        return json.dumps(_normalize(val), ensure_ascii=False, sort_keys=True)

    @staticmethod
    def _is_list_of_dicts(val: Any) -> bool:
        return isinstance(val, list) and all(isinstance(item, dict) for item in val)

    @classmethod
    def _find_changes_in_dict_lists(cls, old_list: List[dict], new_list: List[dict], field_name: str) -> List[Change]:
        changes: List[Change] = []

        unmatched_new = set(range(len(new_list)))

        for old_item in old_list:
            best_idx = None
            best_score = None

            for idx in unmatched_new:
                score = cls._difference_score(old_item, new_list[idx])

                if best_score is None or score < best_score:
                    best_score = score
                    best_idx = idx

                if score == 0:
                    break

            if best_idx is None:
                changes.append(Change(
                    field=field_name,
                    old=cls._format_val(old_item),
                    new=None
                ))
                continue

            unmatched_new.remove(best_idx)
            changes.extend(cls.find_changes(old_item, new_list[best_idx], field_name))

        for idx in unmatched_new:
            changes.append(Change(
                field=field_name,
                old=None,
                new=cls._format_val(new_list[idx])
            ))

        return changes

    @classmethod
    def _difference_score(cls, old_val: Any, new_val: Any) -> int:
        if old_val == new_val:
            return 0

        if isinstance(old_val, dict) and isinstance(new_val, dict):
            all_keys = set(old_val.keys()) | set(new_val.keys())
            return sum(cls._difference_score(old_val.get(key), new_val.get(key)) for key in all_keys)

        if isinstance(old_val, list) and isinstance(new_val, list):
            return 0 if cls._canonical(old_val) == cls._canonical(new_val) else abs(len(old_val) - len(new_val)) + 1

        return 1