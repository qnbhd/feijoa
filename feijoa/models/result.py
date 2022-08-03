from typing import Dict
from typing import Optional

from pydantic import BaseModel


class Result(BaseModel):
    objective_result: float
    metrics: Optional[Dict[str, float]]
