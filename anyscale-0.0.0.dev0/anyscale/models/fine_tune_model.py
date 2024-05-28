from typing import Optional

from anyscale.anyscale_pydantic import BaseModel


class FineTuneConfig(BaseModel):
    base_model: str
    train_file: str
    valid_file: Optional[str]
    cloud_id: str
    suffix: Optional[str]
    version: Optional[str]
    instance_type: Optional[str]
