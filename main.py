import asyncio
import aiohttp
import argparse
import datetime
import aiofile

class CurrencyService:
    PRIVATBANK_API_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def get_currency_rate(self, date: str = None):
        if not date:
            date = datetime.datetime.now().strftime("%d.%m.%Y")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.PRIVATBANK_API_URL}?json&date={date}") as response:
                data = await response.json()
                return data

    async def get_currency_rates_for_last_days(self, days: int, currencies: list = ["EUR", "USD"]):
        currency_rates = []
        for i in range(days):
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d.%m.%Y")
            currency_rate = await self.get_currency_rate(date)
            selected_currencies = {currency: currency_rate["exchangeRate"].get(currency) for currency in currencies}
            currency_rates.append({date: selected_currencies})
        return currency_rates

async def main(days: int):
    service = CurrencyService()
    currency_rates = await service.get_currency_rates_for_last_days(days)
    print(currency_rates)

async def ws_exchange_command(message: str):
    if message.strip().lower() == "exchange":
        service = CurrencyService()
        currency_rates = await service.get_currency_rates_for_last_days(2)
        formatted_rates = "\n".join([f"{date}: {rates}" for rate in currency_rates for date, rates in rate.items()])
        await log_exchange_command()
        return formatted_rates
    return None

async def log_exchange_command():
    async with aiofile.async_open("exchange.log", mode="a") as f:
        await f.write(f"Exchange command executed at {datetime.datetime.now()}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get currency rates for the last few days")
    parser.add_argument("days", type=int, help="Number of days to get currency rates for")
    args = parser.parse_args()
    
    asyncio.run(main(args.days))
