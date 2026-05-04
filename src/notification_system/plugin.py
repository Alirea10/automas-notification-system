from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from plyer import notification

if TYPE_CHECKING:
    from mas.plugins import PluginContext

from .schema import Config


SUMMARY_LIMIT = 300


class SystemChannel:
    def __init__(self, ctx: "PluginContext", config: Config) -> None:
        self.ctx = ctx
        self.config = config

    async def send(self, payload: dict[str, Any]) -> bool:
        if not self.config.enabled:
            return False

        title = str(payload.get("title") or "AUTO-MAS 通知")
        message = self._append_extra_summary(str(payload.get("text") or ""), payload)
        timeout = int(payload.get("timeout") or self.config.timeout)
        ticker = str(payload.get("ticker") or title)

        if notification.notify is None:
            self.ctx.logger.error("plyer.notification 不可用")
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
        self.ctx.logger.info(f"系统通知已发送: {title}")
        return True

    def _append_extra_summary(self, message: str, payload: dict[str, Any]) -> str:
        summary = self._render_extra_summary(payload, SUMMARY_LIMIT)
        if not summary:
            return message
        return f"{message}\n\n{summary}"

    def _render_extra_summary(self, payload: dict[str, Any], limit: int) -> str:
        extra = payload.get("extra")
        if not isinstance(extra, dict):
            return ""

        parts: list[str] = []
        for index, item in enumerate(extra.get("logs") or [], start=1):
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or f"log-{index}.txt")
            content = str(item.get("content") or "")
            parts.append(f"[日志: {name}] {content}")

        for key, label in (("images", "图片"), ("attachments", "附件")):
            for index, item in enumerate(extra.get(key) or [], start=1):
                if not isinstance(item, dict):
                    continue
                name = str(item.get("caption") or item.get("name") or item.get("path") or f"{key}-{index}")
                parts.append(f"[{label}: {name}]")

        summary = "\n".join(parts).strip()
        if len(summary) > limit:
            return summary[: max(0, limit - 3)] + "..."
        return summary


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
        self.ctx.logger.info("通道已启动")

    async def on_stop(self, reason: str) -> None:
        notify = self.ctx.get("notify")
        if notify is not None:
            notify.unregister_channel("system")
        self.ctx.logger.info(f"插件停止, reason={reason}")
