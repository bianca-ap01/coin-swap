import httpx
from fastapi import HTTPException
from abc import ABC, abstractmethod

class CurrencyAPIAdapter(ABC):
    @abstractmethod
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        pass

    @abstractmethod
    def name(self) -> str:
        pass

class ExchangeRateApiComAdapter(CurrencyAPIAdapter):
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            if to_currency not in rates:
                raise HTTPException(400, f"Moneda {to_currency} no soportada")
            return rates[to_currency]

    def name(self) -> str:
        return "ExchangeRate-API.com (public)"

class OpenERAPIAdapter(CurrencyAPIAdapter):
    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        url = "https://open.er-api.com/v6/latest/USD"
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            if data.get("result") != "success":
                raise HTTPException(500, "No se pudo obtener tasa de cambio")
            rates = data.get("rates", {})
            try:
                rate_from = rates[from_currency]
                rate_to = rates[to_currency]
            except KeyError:
                raise HTTPException(400, "Moneda no soportada")
            return rate_to / rate_from

    def name(self) -> str:
        return "Open ER API (public)"

class CurrencyAPIClientSingleton:
    _instance = None
    _adapters: dict = {}
    _current_adapter_key: str = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._adapters = {
                "exchangerateapi": ExchangeRateApiComAdapter(),
                "openerapublic": OpenERAPIAdapter(),
            }
            cls._instance._current_adapter_key = "exchangerateapi"
        return cls._instance

    def select_adapter(self, key: str):
        if key not in self._adapters:
            raise ValueError(f"Adaptador '{key}' no disponible")
        self._current_adapter_key = key

    def get_current_adapter_name(self) -> str:
        return self._adapters[self._current_adapter_key].name()

    async def get_rate(self, from_currency: str, to_currency: str) -> float:
        adapter = self._adapters[self._current_adapter_key]
        return await adapter.get_rate(from_currency, to_currency)

    async def list_all_rates(self, from_currency: str, to_currency: str) -> dict:
        rates = {}
        for adapter in self._adapters.values():
            try:
                rate = await adapter.get_rate(from_currency, to_currency)
                rates[adapter.name()] = rate
            except Exception as e:
                rates[adapter.name()] = f"Error: {str(e)}"
        return rates

currency_api_client = CurrencyAPIClientSingleton()
