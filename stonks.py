import asyncio
import json
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from aiohttp import ClientSession
from aiohttp import ClientTimeout
import pandas as pd


class AbstractParser(ABC):
    def __init__(self, session: ClientSession, sem: asyncio.Semaphore):
        self.session = session
        self.sem = sem

    async def parse(self, url: str):
        html = await self.fetch_page(url)
        soup = self.pre_process(html)
        return self.parse_content(soup)

    async def fetch_page(self, url: str) -> str:
        async with self.sem:
            async with self.session.get(url) as response:
                return await response.text()

    def pre_process(self, html: str):
        return BeautifulSoup(html, "html.parser")

    @abstractmethod
    def parse_content(self, soup: BeautifulSoup):
        pass


# функция для безопасного преобразования
def safe_parse_float(text: str) -> float | None:
    try:
        clean = text.strip().replace(",", "").replace("\n", "")
        # убрать все нецифровые символы, кроме точки и минуса
        import re
        clean = re.sub(r"[^0-9\.\-]", "", clean)
        return float(clean)
    except (ValueError, TypeError):
        return None

class MainPageParser(AbstractParser):
    SP500_URL = "https://markets.businessinsider.com/index/components/s&p_500"
    COMPANY_URL = "https://markets.businessinsider.com"

    async def parse_main_page(self):
        return await self.parse(self.SP500_URL)

    def parse_content(self, soup: BeautifulSoup):
        companies = []
        table = soup.find("table")
        if not table:
            return companies

        rows = table.find_all("tr")
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 5:
                continue

            a_tag = cols[0].find("a")
            if not a_tag:
                continue

            name = a_tag.text.strip()
            company_link = a_tag.get("href")
            if company_link and not company_link.startswith("http"):
                company_link = self.COMPANY_URL + company_link

            try:
                latest_close = cols[1].text.strip().split("\n")[0]
                price_usd = safe_parse_float(latest_close)
            except ValueError:
                price_usd = None

            try:
                growth_text = cols[7].text.strip().split("\n")[1].replace("%", "")
                growth = safe_parse_float(growth_text)
            except (ValueError, IndexError):
                growth = None

            companies.append(
                {
                    "name": name,
                    "details_url": company_link,
                    "price_usd": price_usd,
                    "growth": growth,
                }
            )
        return companies


class CompanyDetailsParser(AbstractParser):
    async def parse_company_details(self, company_url: str):
        return await self.parse(company_url)

    def parse_content(self, soup: BeautifulSoup):
        code_elem = soup.find("span", class_="price-section__category")
        code = None
        if code_elem:
            inner_span = code_elem.find("span")
            if inner_span:
                code = inner_span.text.replace(",", "").strip()

        pe = None
        pe_label = soup.find("div", class_="snapshot__header", string="P/E Ratio")
        if pe_label:
            try:
                pe = safe_parse_float(pe_label.parent.text.replace("P/E Ratio", "").strip())
            except ValueError:
                pe = None

        week_low, week_high = None, None
        low_elem = soup.find("div", class_="snapshot__header", string="52 Week Low")
        high_elem = soup.find("div", class_="snapshot__header", string="52 Week High")
        try:
            if low_elem:
                week_low = safe_parse_float(
                    low_elem.parent.text.replace("52 Week Low", "").strip()
                )
            if high_elem:
                week_high = safe_parse_float(
                    high_elem.parent.text.replace("52 Week High", "").strip()
                )
        except ValueError:
            week_low, week_high = None, None

        return {
            "code": code,
            "pe": pe,
            "52_week_low": week_low,
            "52_week_high": week_high,
        }


class CBRRateFetcher:
    CBR_URL = "http://www.cbr.ru/scripts/XML_daily.asp"

    def __init__(self, session: ClientSession):
        self.session = session

    async def fetch_rate(self, currency_code: str = "USD") -> safe_parse_float:
        async with self.session.get(self.CBR_URL) as response:
            xml_text = await response.text()
            root = ET.fromstring(xml_text)
            for valute in root.findall("Valute"):
                code = valute.find("CharCode").text
                if code == currency_code:
                    value_str = valute.find("Value").text
                    return safe_parse_float(value_str.replace(",", "."))
        raise Exception(f"Currency {currency_code} not found")


class MarketScraper:
    def __init__(
        self,
        session: ClientSession,
        sem: asyncio.Semaphore,
        cbr_fetcher: CBRRateFetcher,
        main_parser: MainPageParser,
        company_parser: CompanyDetailsParser,
    ):
        self.session = session
        self.sem = sem
        self.cbr_fetcher = cbr_fetcher
        self.main_parser = main_parser
        self.company_parser = company_parser

    async def run(self) -> None:
        conversion_rate = await self.cbr_fetcher.fetch_rate("USD")

        companies = await self.main_parser.parse_main_page()

        for comp in companies:
            price_usd = comp.get("price_usd")
            comp["price_rub"] = (
                price_usd * conversion_rate if price_usd is not None else None
            )

        tasks = [
            self.company_parser.parse_company_details(comp["details_url"])
            for comp in companies
        ]
        details_list = await asyncio.gather(*tasks)

        for comp, details in zip(companies, details_list):
            comp.update(details)
            low = comp.get("52_week_low")
            high = comp.get("52_week_high")
            if low and high and low != 0:
                comp["potential_profit"] = ((high - low) / low) * 100
            else:
                comp["potential_profit"] = None

        companies = [
            c
            for c in companies
            if c.get("price_rub") is not None
            and c.get("pe") is not None
            and c.get("growth") is not None
            and c.get("potential_profit") is not None
        ]

        top_price = sorted(companies, key=lambda x: x["price_rub"], reverse=True)[:10]
        top_pe = sorted(companies, key=lambda x: x["pe"])[:10]
        top_growth = sorted(companies, key=lambda x: x["growth"], reverse=True)[:10]
        top_profit = sorted(
            companies, key=lambda x: x["potential_profit"], reverse=True
        )[:10]

        with open("top_10_highest_prices.json", "w", encoding="utf-8") as f:
            json.dump(top_price, f, indent=4, ensure_ascii=False)
        with open("top_10_lowest_pe.json", "w", encoding="utf-8") as f:
            json.dump(top_pe, f, indent=4, ensure_ascii=False)
        with open("top_10_highest_growth.json", "w", encoding="utf-8") as f:
            json.dump(top_growth, f, indent=4, ensure_ascii=False)
        with open("top_10_potential_profit.json", "w", encoding="utf-8") as f:
            json.dump(top_profit, f, indent=4, ensure_ascii=False)

        print("Данные сохранены в JSON файлах.")

        df = pd.DataFrame(companies)
        df.to_csv("output.csv", sep=";", index=False, encoding="utf-8-sig")

        print("А также в csv.")


class MarketScraperFactory:
    @staticmethod
    async def create(semaphore_limit: int = 10) -> MarketScraper:
        sem = asyncio.Semaphore(semaphore_limit)
        timeout = ClientTimeout(total=10)  # максимум 10 сек.
        session = ClientSession(timeout=timeout)
        cbr_fetcher = CBRRateFetcher(session)
        main_parser = MainPageParser(session, sem)
        company_parser = CompanyDetailsParser(session, sem)
        return MarketScraper(session, sem, cbr_fetcher, main_parser, company_parser)


async def main():
    scraper = await MarketScraperFactory.create(semaphore_limit=10)
    try:
        await scraper.run()
    finally:
        await scraper.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nПрервано пользователем.")
