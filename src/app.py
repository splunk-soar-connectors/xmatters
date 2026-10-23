# Copyright (c) 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from soar_sdk.app import App
from soar_sdk.asset import BaseAsset, AssetField
from soar_sdk.logging import getLogger

logger = getLogger()


class Asset(BaseAsset):
    base_url: str = AssetField(
        description="Base url, e.g. https://my-company.xmatters.com"
    )
    username: str = AssetField(description="Username")
    password: str = AssetField(description="Password", sensitive=True)
    client_id: str | None = AssetField(
        description="Client ID. OAuth will be preferred if provided"
    )


app = App(
    name="xMatters for SOAR",
    app_type="devops",
    logo="logo_xmatters.svg",
    logo_dark="logo_xmatters_dark.svg",
    product_vendor="xMatters",
    product_name="xMatters",
    publisher="Splunk",
    appid="60e80285-8850-417a-9617-2423d6b9ca76",
    fips_compliant=True,
    asset_cls=Asset,
)

from . import actions  # noqa: F401


if __name__ == "__main__":
    app.cli()
