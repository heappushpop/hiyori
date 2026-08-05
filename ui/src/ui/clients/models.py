from base64 import b64encode
from json import dumps
from math import pi
from os import environ
from urllib.parse import quote, urlencode
from uuid import uuid4
from zoneinfo import ZoneInfo
import datetime

from bokeh.embed import components
from bokeh.layouts import Spacer, column
from bokeh.models import ColumnDataSource, CustomJS, DatetimeRangePicker, HoverTool
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.plotting import figure
from django.db.models import CharField, DateTimeField, IntegerField, Model, UUIDField
from django.urls import reverse
from pandas import DataFrame

from ui.settings import TIME_ZONE
from xray.api import Xray


class Client(Model):
    created_at = DateTimeField(auto_now_add=True)
    level = IntegerField(default=0)
    name = CharField(unique=True)
    uuid = UUIDField(default=uuid4, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("clients:client", args=[self.id])

    def plot(self):
        data = DataFrame(
            self.stat_set.order_by("created_at").values("created_at", "down", "up")
        )

        if data.empty:
            return

        data["created_at"] = (
            data["created_at"].dt.tz_convert(TIME_ZONE).dt.tz_localize(None)
        )
        data["down"] = data["down"].expanding().sum()
        data["up"] = data["up"].expanding().sum()

        end = datetime.datetime.now(datetime.UTC)
        start = end - datetime.timedelta(days=7)

        date_range_picker = DatetimeRangePicker(
            margin=0,
            sizing_mode="scale_width",
            title="Select time period",
            value=(start, end),
        )

        source = ColumnDataSource(data)

        plot = figure(
            height=380,
            sizing_mode="scale_width",
            tools=["xpan", "xwheel_zoom", "reset"],
            x_axis_type="datetime",
            x_range=(
                start.astimezone(ZoneInfo(TIME_ZONE)),
                end.astimezone(ZoneInfo(TIME_ZONE)),
            ),
        )

        down_line = plot.line(
            color="tomato",
            legend_label="Down",
            line_width=2,
            source=source,
            x="created_at",
            y="down",
        )

        up_line = plot.line(
            color="skyblue",
            legend_label="Up",
            line_width=2,
            source=source,
            x="created_at",
            y="up",
        )

        plot.legend.background_fill_alpha = 0.8
        plot.legend.location = "top_left"
        plot.legend.orientation = "horizontal"
        plot.xaxis.major_label_orientation = pi / 4
        plot.yaxis.formatter = NumeralTickFormatter(format="0.0b")

        plot.add_tools(
            HoverTool(
                description="Down hover",
                mode="vline",
                renderers=[down_line],
                tooltips=[("Down", "@down{0.0b}")],
            )
        )

        plot.add_tools(
            HoverTool(
                description="Up hover",
                mode="vline",
                renderers=[up_line],
                tooltips=[("Up", "@up{0.0b}")],
            )
        )

        date_range_picker.js_on_change(
            "value",
            CustomJS(
                args={"x_range": plot.x_range},
                code="\n".join(
                    [
                        'x_range.start = luxon.DateTime.fromISO(this.value[0], { zone: "utc" }).toMillis();',
                        'x_range.end = luxon.DateTime.fromISO(this.value[1], { zone: "utc" }).toMillis();',
                    ]
                ),
            ),
        )

        return "".join(
            components(
                column(
                    date_range_picker,
                    Spacer(height=11),
                    plot,
                    sizing_mode="scale_width",
                )
            )
        )

    def save(self, **kwargs):
        super().save(**kwargs)
        Xray().add_user(
            {
                "email": self.name,
                "flow": f'{environ["XRAY_VLESS_FLOW"]}',
                "id": str(self.uuid),
                "level": self.level,
            }
        )

    def stats(self):
        res = {
            "down": {"day": 0, "month": 0, "year": 0, "total": 0},
            "up": {"day": 0, "month": 0, "year": 0, "total": 0},
        }

        data = DataFrame(
            self.stat_set.order_by("created_at").values("created_at", "down", "up")
        )

        if data.empty:
            return res

        data["created_at"] = (
            data["created_at"].dt.tz_convert(TIME_ZONE).dt.tz_localize(None)
        )

        now = datetime.datetime.now(ZoneInfo(TIME_ZONE))

        day = data[data["created_at"] >= str(now.date())]
        res["down"]["day"] = day["down"].sum().item()
        res["up"]["day"] = day["up"].sum().item()

        month = data[data["created_at"] >= str(now.replace(day=1).date())]
        res["down"]["month"] = month["down"].sum().item()
        res["up"]["month"] = month["up"].sum().item()

        year = data[data["created_at"] >= str(now.replace(month=1, day=1).date())]
        res["down"]["year"] = year["down"].sum().item()
        res["up"]["year"] = year["up"].sum().item()

        res["down"]["total"] = data["down"].sum().item()
        res["up"]["total"] = data["up"].sum().item()

        return res

    def vless(self):
        userinfo = quote(str(self.uuid))
        host = environ["DOMAIN_NAME"]
        port = "443"
        query = urlencode(
            {
                "type": "xhttp",
                "encryption": f'{environ["XRAY_VLESS_ENCRYPTION"]}',
                "flow": f'{environ["XRAY_VLESS_FLOW"]}',
                "security": "tls",
                "path": f'{environ["XRAY_VLESS_PATH"]}',
                "sni": host,
                "alpn": "h3",
            }
        )
        fragment = quote(host)

        return f"vless://{userinfo}@{host}:{port}?{query}#{fragment}"

    def vmess(self):
        host = environ["DOMAIN_NAME"]
        port = "443"
        encoded = b64encode(
            dumps(
                {
                    "v": "2",
                    "ps": host,
                    "add": host,
                    "port": port,
                    "id": str(self.uuid),
                    "aid": "0",
                    "net": "xhttp",
                    "type": "none",
                    "host": host,
                    "path": f'{environ["XRAY_VMESS_PATH"]}',
                    "tls": "tls",
                    "sni": host,
                    "alpn": "h3",
                }
            ).encode()
        ).decode()

        return f"vmess://{encoded}"
