import re
from urllib.parse import urlparse


class ChromeProxyExtension:
    def __init__(self, proxy_link, proxy_folder_path):
        if not self._validate_proxy_link(proxy_link):
            raise ValueError("Invalid proxy link format. Expected format: http[s]://[user:password@]host[:port]")

        self._parse_proxy_link(proxy_link)
        self.proxy_folder = proxy_folder_path

    def _validate_proxy_link(self, proxy_link):
        regex = r'^http[s]?://(?:[A-Za-z0-9._~%-]+:[A-Za-z0-9._~%-]+@)?[A-Za-z0-9.-]+(?::\d{1,5})?$'
        return re.match(regex, proxy_link) is not None

    def _parse_proxy_link(self, proxy_link):
        parsed_link = urlparse(proxy_link)

        self.proxy_host = parsed_link.hostname
        self.proxy_port = parsed_link.port if parsed_link.port else 80
        self.proxy_user = parsed_link.username
        self.proxy_pass = parsed_link.password

    def proxy_connection(self):
        if self.proxy_host is None or self.proxy_port is None or self.proxy_user is None \
                or self.proxy_user is None or self.proxy_pass is None or self.proxy_folder is None:
            raise ValueError("Proxy connection isn't possible")
        else:
            manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
            """

            background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: ["localhost"]
                        }
                    };
                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }
                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """ % (self.proxy_host, self.proxy_port, self.proxy_user, self.proxy_pass)

            with open(f"{self.proxy_folder}/manifest.json", "w") as f:
                f.write(manifest_json)
            with open(f"{self.proxy_folder}/background.js", "w") as f:
                f.write(background_js)