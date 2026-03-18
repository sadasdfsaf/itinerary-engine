import re

from itinerary_engine.schema.models import EditIntent


class EditParseError(ValueError):
    pass


class RuleBasedEditParser:
    def parse(self, instruction: str) -> EditIntent:
        text = instruction.strip()
        if not text:
            raise EditParseError("Instruction is empty.")

        lowered = text.lower()

        replace_patterns = [
            re.compile(
                r"replace\s+(?P<target>.+?)\s+on\s+day\s*(?P<day>\d+)\s+with\s+(?P<replacement>.+)",
                re.I,
            ),
            re.compile(
                r"(?:day\s*(?P<day>\d+).*)?replace\s+(?P<target>.+?)\s+with\s+(?P<replacement>.+)",
                re.I,
            ),
            re.compile(r"(?:第(?P<day>\d+)天.*)?把(?P<target>.+?)换成(?P<replacement>.+)"),
        ]
        for pattern in replace_patterns:
            match = pattern.search(text)
            if match:
                day = match.groupdict().get("day")
                return EditIntent(
                    action="replace",
                    user_instruction=text,
                    target_day=int(day) if day else None,
                    target_text=self._clean_phrase(match.group("target")),
                    replacement_text=self._clean_phrase(match.group("replacement")),
                    confidence=0.91,
                )

        move_patterns = [
            re.compile(r"move\s+(?P<target>.+?)\s+to\s+day\s*(?P<day>\d+)", re.I),
            re.compile(r"把(?P<target>.+?)移到第(?P<day>\d+)天"),
        ]
        for pattern in move_patterns:
            match = pattern.search(text)
            if match:
                return EditIntent(
                    action="move",
                    user_instruction=text,
                    target_day=int(match.group("day")),
                    target_text=self._clean_phrase(match.group("target")),
                    confidence=0.88,
                )

        remove_patterns = [
            re.compile(
                r"(?:remove|delete)\s+(?P<target>.+?)(?:\s+on\s+day\s*(?P<day>\d+))?$",
                re.I,
            ),
            re.compile(r"(?:第(?P<day>\d+)天.*)?删除(?P<target>.+)"),
        ]
        for pattern in remove_patterns:
            match = pattern.search(text)
            if match:
                day = match.groupdict().get("day")
                return EditIntent(
                    action="remove",
                    user_instruction=text,
                    target_day=int(day) if day else None,
                    target_text=self._clean_phrase(match.group("target")),
                    confidence=0.89,
                )

        insert_patterns = [
            re.compile(
                r"(?:add|insert)\s+(?P<replacement>.+?)(?:\s+on\s+day\s*(?P<day>\d+))?$",
                re.I,
            ),
            re.compile(r"(?:第(?P<day>\d+)天.*)?(?:加上|增加)(?P<replacement>.+)"),
        ]
        for pattern in insert_patterns:
            match = pattern.search(text)
            if match:
                day = match.groupdict().get("day")
                return EditIntent(
                    action="insert",
                    user_instruction=text,
                    target_day=int(day) if day else 1,
                    replacement_text=self._clean_phrase(match.group("replacement")),
                    confidence=0.84,
                )

        if any(
            keyword in lowered
            for keyword in ["slow down", "less packed", "more relaxed", "轻松", "别太赶"]
        ):
            return EditIntent(action="slow_down", user_instruction=text, confidence=0.8)

        if any(
            keyword in lowered
            for keyword in ["cheaper", "lower budget", "save money", "省钱", "便宜一点"]
        ):
            return EditIntent(action="tighten_budget", user_instruction=text, confidence=0.8)

        raise EditParseError("Instruction does not match a supported edit pattern.")

    def _clean_phrase(self, value: str) -> str:
        cleaned = value.strip().strip(".,!?;:，。！？；：、")
        lowered = cleaned.lower()
        for prefix in ("the ", "a ", "an "):
            if lowered.startswith(prefix):
                return cleaned[len(prefix):].strip(".,!?;:，。！？；：、 ")
        return cleaned
