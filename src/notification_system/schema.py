from mas.plugin_config import PluginField
from pydantic import BaseModel, ConfigDict


class Config(BaseModel):
    model_config = ConfigDict(extra="allow")

    enabled: bool = PluginField(
        default=True,
        description="启用系统通知",
        json_schema_extra={"group": "basic", "order": 1},
    )
    app_name: str = PluginField(
        default="AUTO-MAS",
        description="应用名称",
        json_schema_extra={"group": "basic", "order": 2},
    )
    timeout: int = PluginField(
        default=3,
        ge=1,
        description="默认显示秒数",
        json_schema_extra={"group": "basic", "min": 1, "step": 1, "order": 3},
    )
