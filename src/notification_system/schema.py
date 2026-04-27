from pydantic import BaseModel, ConfigDict, Field


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    enabled: bool = Field(
        default=True,
        description="启用系统通知",
        json_schema_extra={"group": "basic", "order": 1},
    )
    app_name: str = Field(
        default="AUTO-MAS",
        description="应用名称",
        json_schema_extra={"group": "basic", "order": 2},
    )
    timeout: int = Field(
        default=3,
        ge=1,
        description="默认显示秒数",
        json_schema_extra={"group": "basic", "min": 1, "step": 1, "order": 3},
    )
