"""Optional real-browser verification; run both local servers first (see docs/qa/verification.md)."""

import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def run(args):
    shots = Path(args.screenshots)
    shots.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as playwright:
        options = {"headless": True}
        if args.chromium:
            options["executable_path"] = args.chromium
        browser = await playwright.chromium.launch(**options)
        context = await browser.new_context(viewport={"width": 1440, "height": 1000})
        page = await context.new_page()
        report = {}
        for width in [320, 390, 768, 1440]:
            await page.set_viewport_size({"width": width, "height": 1000})
            for route in ["/", "/articles/", "/tags/", "/articles/long-title/", "/articles/reading-check/"]:
                await page.goto(args.fixture + route)
                await page.evaluate("document.fonts.ready")
                assert not await page.evaluate("document.documentElement.scrollWidth > innerWidth"), (
                    width,
                    route,
                )
        assert await page.locator(".language-switch").count() == 0
        assert await page.locator("html").get_attribute("lang") == "en"
        report["responsive"] = (
            "320, 390, 768 and 1440px: English index, topics and articles have no page overflow"
        )
        await page.goto(args.fixture + "/")
        await page.evaluate("window.__documentMarker = 'preserved'")
        await page.locator("#article-search").fill("verifiable")
        await page.wait_for_function("() => document.querySelector('#posts').dataset.resultCount === '1'")
        assert await page.evaluate("window.__documentMarker") == "preserved"
        assert await page.evaluate("document.activeElement.id") == "article-search"
        assert await page.locator("#search-status").inner_text() == "1 article"
        await page.reload()
        assert await page.locator("#article-search").input_value() == "verifiable"
        await page.locator(".post-title-link").click()
        await page.go_back()
        assert await page.locator("#article-search").input_value() == "verifiable"
        report["htmx"] = "fragment update, focus, live count, reload and native back navigation passed"
        await page.route("**/?q=broken-query*", lambda route: route.abort())
        await page.locator("#article-search").fill("broken-query")
        await page.locator("#search-error").wait_for(state="visible")
        assert await page.locator("#posts").get_attribute("data-result-count") == "1"
        await page.unroute("**/?q=broken-query*")
        await page.locator("#article-search").fill("not-a-match")
        await page.wait_for_function("() => document.querySelector('#posts').dataset.resultCount === '0'")
        assert await page.locator("#search-error").is_hidden()
        report["recovery"] = (
            "failed request kept prior results, showed recovery, then successful search cleared error"
        )
        await page.goto(args.fixture + "/articles/reading-check/")
        await page.set_viewport_size({"width": 320, "height": 800})
        assert await page.get_by_role("table").count() == 1
        assert await page.locator("table").get_attribute("role") is None
        assert await page.locator(".table-scroll[role=region][tabindex='0']").count() == 1
        await page.emulate_media(reduced_motion="reduce")
        assert await page.evaluate("getComputedStyle(document.documentElement).scrollBehavior") == "auto"
        await page.evaluate("""() => {for(const e of document.querySelectorAll('*')) {
          e.style.setProperty('line-height','1.5','important');
          e.style.setProperty('letter-spacing','.12em','important');
          e.style.setProperty('word-spacing','.16em','important');
        } for(const e of document.querySelectorAll('p'))e.style.setProperty('margin-bottom','2em','important');} """)
        assert not await page.evaluate("document.documentElement.scrollWidth > innerWidth")
        report["reading"] = (
            "native table semantics, focusable overflow, reduced motion and text-spacing override passed"
        )
        for name, origin, route, width in [
            ("home-desktop", args.base, "/", 1440),
            ("home-mobile", args.base, "/", 390),
            ("article-desktop", args.fixture, "/articles/reading-check/", 1440),
            ("article-mobile", args.fixture, "/articles/reading-check/", 390),
            ("list-mobile", args.fixture, "/", 320),
        ]:
            await page.set_viewport_size({"width": width, "height": 1000 if width == 1440 else 844})
            await page.goto(origin + route)
            await page.evaluate("document.fonts.ready")
            await page.screenshot(path=str(shots / (name + ".png")), full_page=True)
        await page.goto(args.base + "/about/")
        assert await page.get_by_role("link", name="PACE Mobility GmbH").count() == 1
        await page.keyboard.press("Tab")
        assert await page.evaluate("document.activeElement.className") == "skip-link"
        await page.keyboard.press("Enter")
        assert await page.evaluate("document.activeElement.id") == "content"
        report["keyboard"] = "skip link moves focus to content; public professional link preserved"
        nojs_context = await browser.new_context(
            java_script_enabled=False, viewport={"width": 390, "height": 844}
        )
        nojs = await nojs_context.new_page()
        await nojs.goto(args.fixture + "/")
        await nojs.locator("#article-search").fill("verifiable")
        await nojs.get_by_role("button", name="Search", exact=True).click()
        await nojs.wait_for_url("**/?q=*")
        assert await nojs.locator("#posts").get_attribute("data-result-count") == "1"
        assert await nojs.evaluate("typeof htmx") == "undefined"
        report["noJavaScript"] = "ordinary GET search returns correct result with browser JavaScript disabled"
        print(json.dumps(report, indent=2))
        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default="http://127.0.0.1:8000")
    parser.add_argument("--fixture", default="http://127.0.0.1:8001")
    parser.add_argument("--chromium")
    parser.add_argument("--screenshots", default="/tmp/personal-blog-qa")
    asyncio.run(run(parser.parse_args()))
