from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List
import json


@dataclass
class AlternativeExplanation:
    type: str
    explanation: str
    possible_variables: List[str] = field(default_factory=list)
    validation_method: str = ""


@dataclass
class HypothesisResult:
    hypothesis: Dict[str, Any]
    alternative_explanations: List[AlternativeExplanation]
    recommended_validation: List[str]
    limitations: List[str]
    generation_confidence: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)
