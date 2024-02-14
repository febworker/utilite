import asyncio
import aiohttp
import argparse
import datetime
import aiofiles
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)


class CurrencyService:
    PRIVATBANK_API_URL = "https://api.privatbank.ua/#p24/exchangeArchive"

    async def get_currency_rate(self, date: str = None):
        if not date:
            date = datetime.datetime.now().strftime("%d.%m.%Y")

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.PRIVATBANK_API_URL}?json&date={date}") as response:
                data = await response.json()
                return data

    async def get_currency_rates_for_last_days(self, days: int, currencies: list = ["USD", "EUR", "CHF", "GBP", "PLZ", "SEK", "XAU", "CAD"]):
        currency_rates = []
        for i in range(min(days, 10)):  # Обмежуємо кількість днів до 10
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d.%m.%Y")
            currency_rate = await self.get_currency_rate(date)
            selected_currencies = {currency: currency_rate["exchangeRate"].get(currency) for currency in currencies}
            currency_rates.append({date: selected_currencies})
        return currency_rates


class ChatServer:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            async for message in ws:
                if message.strip().lower() == "exchange":
                    service = CurrencyService()
                    currency_rates = await service.get_currency_rates_for_last_days(2)
                    formatted_rates = "\n".join(
                        [f"{date}: {rates}" for rate in currency_rates for date, rates in rate.items()])
                    await ws.send(formatted_rates)
                else:
                    await self.send_to_clients(f"{ws.name}: {message}")
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)


async def main(days: int):
    server = ChatServer()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Get currency rates for the last few days")
    parser.add_argument("days", type=int, help="Number of days to get currency rates for (maximum 10)")
    args = parser.parse_args()

    if args.days > 10:
        print("Error: Number of days should be maximum 10.")
        exit()

    asyncio.run(main(args.days))
