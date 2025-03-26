from pydantic import BaseModel, constr
from typing import Annotated

class CelularSchema(BaseModel):
    numero: Annotated[str, constr(min_length=1, max_length=20)]
    app_id: int
    api_hash: Annotated[str, constr(min_length=1, max_length=50)]
    nombre: Annotated[str, constr(min_length=1, max_length=100)]
