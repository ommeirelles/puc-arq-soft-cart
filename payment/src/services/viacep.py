import requests
from os import environ
from unicodedata import normalize, combining
from pydantic import BaseModel
from schemas import Address

class ViaCepAddress(BaseModel):
    """
        Address returned by the ViaCEP public API
    """
    cep: str
    logradouro: str
    bairro: str
    localidade: str
    uf: str
    erro: bool = False

class ViaCepService:
    __api = environ.get("VIA_CEP_API_URL", "https://viacep.com.br")

    def getAddress(self, cep: str) -> ViaCepAddress | None:
        """
            Looks up a CEP in the ViaCEP public API, returning None
            when the CEP does not exist
        """
        response = requests.get(
            f"{self.__api}/ws/{cep.replace('-', '')}/json/",
            timeout=10
        )
        if (response.status_code != 200):
            raise Exception("ViaCEP service unavailable")

        data = response.json()
        if (data.get("erro") in (True, "true")):
            return None

        return ViaCepAddress(**data)

    def matches(self, viaCep: ViaCepAddress, address: Address) -> bool:
        """
            Cross-checks the informed city and state against the CEP data
        """
        return self.__normalize(viaCep.localidade) == self.__normalize(address.city) \
            and self.__normalize(viaCep.uf) == self.__normalize(address.state)

    def __normalize(self, value: str) -> str:
        return "".join(
            char for char in normalize("NFD", value) if not combining(char)
        ).strip().lower()
