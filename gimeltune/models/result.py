from typing import Optional, Dict

from pydantic import BaseModel


class Result(BaseModel):
    objective_result: float
    metrics: Optional[Dict[str, float]]
