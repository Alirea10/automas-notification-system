from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from plyer import notification

if TYPE_CHECKING:
    from mas.plugins import PluginContext

from .schema import Config


class SystemChannel:
    def __init__(self, ctx: "PluginContext", config: Config) -> None:
        self.ctx = ctx
        self.config = config

    async def send(self, payload: dict[str, Any]) -> bool:
        if not self.config.enabled:
            return False

        title = str(payload.get("title") or "AUTO-MAS 通知")
        message = str(payload.get("text") or "")
        timeout = int(payload.get("timeout") or self.config.timeout)
        ticker = str(payload.get("ticker") or title)

        if notification.notify is None:
            self.ctx.logger.error("[notification_system] plyer.notification 不可用")
            return False

        notification.notify(
            title=title,
            message=message,
            app_name=self.config.app_name,
            app_icon=(Path.cwd() / "res/icons/AUTO-MAS.ico").as_posix(),
            timeout=timeout,
            ticker=ticker,
            toast=True,
        )
        self.ctx.logger.info(f"[notification_system] 系统通知已发送: {title}")
        return True


class Plugin:
    needs = "notify"

    def __init__(self, ctx: "PluginContext") -> None:
        self.ctx = ctx
        self.channel: SystemChannel | None = None

    async def on_start(self) -> None:
        raw_config = self.ctx.config.to_dict() if hasattr(self.ctx.config, "to_dict") else dict(self.ctx.config)
        config = Config.model_validate(raw_config)
        self.channel = SystemChannel(self.ctx, config)
        notify = self.ctx.get("notify")
        notify.register_channel("system", self.channel)
        self.ctx.logger.info("[notification_system] 通道已启动")

    async def on_stop(self, reason: str) -> None:
        notify = self.ctx.get("notify")
        if notify is not None:
            notify.unregister_channel("system")
        self.ctx.logger.info(f"[notification_system] 插件停止, reason={reason}")
