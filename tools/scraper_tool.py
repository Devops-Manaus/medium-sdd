import logging
import time
import trafilatura
from trafilatura import extract
from trafilatura.settings import use_config
from urllib.parse import urlparse

log = logging.getLogger(__name__)

try:
    from curl_cffi import requests as cffi_requests
    HAS_CFFI = True
except ImportError:
    HAS_CFFI = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


class ScraperTool:

    def __init__(
        self,
        max_chars: int = 8000,
        timeout: int = 15,
        use_fallback: bool = True,
        compliant_mode: bool = True,
        max_retries: int = 2,
        browser_user_agent: str = (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
    ):
        self.max_chars = max_chars
        self.timeout = timeout
        self.use_fallback = use_fallback
        self.compliant_mode = compliant_mode
        self.max_retries = max_retries
        self.browser_user_agent = browser_user_agent
        self.config = use_config()
        self.config.set("DEFAULT", "DOWNLOAD_TIMEOUT", str(timeout))
        self.config.set("DEFAULT", "MIN_OUTPUT_SIZE", "200")
        self.playwright_runtime = None
        self.playwright_browser = None
        self.playwright_context_by_domain = {}

    def extract_text(self, url: str) -> dict:
        if HAS_CFFI:
            result = self.cffi_fetch(url)
            if result["status"] == "ok":
                return result
            if result["status"] == "cffi_cloudflare_challenge" and self.use_fallback and HAS_PLAYWRIGHT:
                playwright_result = self.playwright_extract(url)
                if playwright_result["status"] == "ok":
                    return playwright_result

        result = self.trafilatura_extract(url)
        if result["status"] == "ok":
            return result

        if self.use_fallback and HAS_PLAYWRIGHT:
            playwright_result = self.playwright_extract(url)
            if playwright_result["status"] == "ok":
                return playwright_result

        return result

    def cffi_fetch(self, url: str) -> dict:
        last_status = "cffi_failed"
        for attempt_number in range(self.max_retries + 1):
            try:
                response = cffi_requests.get(
                    url,
                    impersonate="chrome",
                    timeout=self.timeout,
                    headers=self.build_browser_headers(url),
                )
                if self.is_cloudflare_challenge(
                    body_text=response.text,
                    status_code=response.status_code,
                ):
                    return {"url": url, "text": "", "status": "cffi_cloudflare_challenge"}

                if response.status_code != 200:
                    last_status = f"cffi_http_{response.status_code}"
                    if response.status_code in {403, 429, 503} and attempt_number < self.max_retries:
                        time.sleep(0.6 * (attempt_number + 1))
                        continue
                    return {"url": url, "text": "", "status": last_status}

                text = extract(
                    response.text,
                    include_links=False,
                    include_images=False,
                    output_format="markdown",
                )

                if not text or len(text) < 100:
                    last_status = "cffi_empty_extract"
                    if attempt_number < self.max_retries:
                        time.sleep(0.35 * (attempt_number + 1))
                        continue
                    return {"url": url, "text": "", "status": last_status}

                return {
                    "url": url,
                    "text": text[: self.max_chars],
                    "status": "ok",
                    "source": "cffi",
                    "truncated": len(text) > self.max_chars,
                }
            except Exception as error:
                last_status = f"cffi_error: {error}"
                log.debug("cffi failed: %s — %s", url, error)
                if attempt_number < self.max_retries:
                    time.sleep(0.4 * (attempt_number + 1))
                    continue
                return {"url": url, "text": "", "status": last_status}

        return {"url": url, "text": "", "status": last_status}

    def trafilatura_extract(self, url: str) -> dict:
        try:
            downloaded = trafilatura.fetch_url(url, config=self.config)
            if not downloaded:
                return {"url": url, "text": "", "status": "fetch_failed"}

            text = extract(
                downloaded,
                include_links=False,
                include_images=False,
                output_format="markdown",
                config=self.config,
            )

            if not text or len(text) < 100:
                return {"url": url, "text": "", "status": "empty_extract"}

            return {
                "url": url,
                "text": text[: self.max_chars],
                "status": "ok",
                "source": "trafilatura",
                "truncated": len(text) > self.max_chars,
            }
        except Exception as e:
            return {"url": url, "text": "", "status": f"trafilatura_error: {e}"}

    def playwright_extract(self, url: str) -> dict:
        try:
            browser_context = self.get_or_create_playwright_context(url)
            page = browser_context.new_page()
            response = page.goto(url, timeout=self.timeout * 1000, wait_until="domcontentloaded")
            page.wait_for_load_state("networkidle", timeout=self.timeout * 1000)
            page_html = page.content()
            page_title = (page.title() or "").strip()
            status_code = response.status if response else 0

            if self.is_cloudflare_challenge(
                body_text=f"{page_title}\n{page_html}",
                status_code=status_code,
            ):
                page.close()
                return {"url": url, "text": "", "status": "cloudflare_challenge"}

            text = page.inner_text("body")
            page.close()

            if not text or len(text) < 100:
                return {"url": url, "text": "", "status": "playwright_empty"}

            return {
                "url": url,
                "text": text[: self.max_chars],
                "status": "ok",
                "source": "playwright",
                "truncated": len(text) > self.max_chars,
            }
        except Exception as error:
            log.warning("playwright fallback failed: %s — %s", url, error)
            return {"url": url, "text": "", "status": f"playwright_error: {error}"}

    def build_browser_headers(self, url: str) -> dict:
        if not self.compliant_mode:
            return {}
        host = self.extract_host(url)
        return {
            "User-Agent": self.browser_user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.7",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Upgrade-Insecure-Requests": "1",
            "DNT": "1",
            "Referer": f"https://{host}/",
        }

    def extract_host(self, url: str) -> str:
        parsed_url = urlparse(url)
        return parsed_url.netloc or "localhost"

    def is_cloudflare_challenge(self, body_text: str, status_code: int = 0) -> bool:
        if not body_text:
            return status_code in {403, 429, 503}
        normalized_body = body_text.lower()
        challenge_markers = (
            "cloudflare",
            "attention required",
            "just a moment",
            "checking your browser",
            "cf-challenge",
            "/cdn-cgi/challenge-platform",
            "verify you are human",
        )
        has_marker = any(challenge_marker in normalized_body for challenge_marker in challenge_markers)
        return has_marker and status_code in {0, 403, 429, 503, 200}

    def get_or_create_playwright_context(self, url: str):
        if not HAS_PLAYWRIGHT:
            raise RuntimeError("Playwright não está instalado")

        if self.playwright_runtime is None:
            self.playwright_runtime = sync_playwright().start()

        if self.playwright_browser is None:
            self.playwright_browser = self.playwright_runtime.chromium.launch(headless=True)

        domain = self.extract_host(url).lower()
        if domain in self.playwright_context_by_domain:
            return self.playwright_context_by_domain[domain]

        if self.compliant_mode:
            browser_context = self.playwright_browser.new_context(
                user_agent=self.browser_user_agent,
                locale="en-US",
                timezone_id="America/New_York",
                viewport={"width": 1366, "height": 768},
                java_script_enabled=True,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9,pt-BR;q=0.7",
                    "DNT": "1",
                },
            )
        else:
            browser_context = self.playwright_browser.new_context()
        self.playwright_context_by_domain[domain] = browser_context
        return browser_context

    def shutdown(self):
        for browser_context in self.playwright_context_by_domain.values():
            try:
                browser_context.close()
            except Exception:
                pass
        self.playwright_context_by_domain = {}

        if self.playwright_browser:
            try:
                self.playwright_browser.close()
            except Exception:
                pass
            self.playwright_browser = None

        if self.playwright_runtime:
            try:
                self.playwright_runtime.stop()
            except Exception:
                pass
            self.playwright_runtime = None

    def __del__(self):
        self.shutdown()
