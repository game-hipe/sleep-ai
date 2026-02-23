import json

from urllib.parse import urljoin
from typing import Callable, TypeVar

from loguru import logger
from httpx import AsyncClient
from bs4 import BeautifulSoup
from pydantic import BaseModel

from .schemas import PageResponse, AccountResponse, ErrorResponse, Node


_T = TypeVar("_T", bound=BaseModel)


class ParamBuilder:
    @staticmethod
    def build_account(short_name: str, author_name: str | None = None):
        return {
            "short_name": short_name,
            "author_name": author_name,
        }

    @staticmethod
    def build_page(
        access_token: str,
        title: str,
        content: list[Node] | list[str],
        author_name: str | None = None,
        author_url: str | None = None,
        return_content: bool = False,
    ):
        result = []
        for x in content:
            if isinstance(x, Node):
                result.append(x.model_dump())
            else:
                result.append(x)

        return {
            "access_token": access_token,
            "title": title,
            "content": json.dumps(result),
            "author_name": author_name,
            "return_content": return_content,
            "author_url": author_url,
        }


class Telegraph:
    base_url = "https://api.telegra.ph"

    CREATE_ACCOUNT_URL = urljoin(base_url, "/createAccount")
    CREATE_PAGE_URL = urljoin(base_url, "/createPage")

    def __init__(self, client: AsyncClient, features: str | None = None):
        self.client = client
        self.features = features or "html.parser"
        self._access_token: str | None = None
        self._username = "ai-memory"

    async def create_account(
        self, short_name: str | None = None, author_name: str | None = None
    ) -> AccountResponse | ErrorResponse:
        logger.info(
            f"Создание аккаунта (short_name={short_name}, author_name={author_name})"
        )
        account = await self._base_fetch(
            self.CREATE_ACCOUNT_URL,
            AccountResponse,
            ParamBuilder.build_account,
            short_name=short_name or self._username,
            author_name=author_name,
        )
        if isinstance(account, ErrorResponse):
            logger.error(
                f"Ошибка во время генерации аккаунта (message={account.error})"
            )
            return account

        self._access_token = account.result.access_token
        logger.success(f"Аккаунт создан (token={account.result.access_token})")
        return account

    async def create_page(
        self,
        title: str,
        content: str,
        access_token: str | None = None,
        author_name: str | None = None,
        author_url: str | None = None,
        return_content: bool = False,
    ) -> PageResponse:
        logger.info(f"Создание страницы (title={title})")
        if access_token is None and not self._access_token:
            logger.debug("Аккаунт не инцилизирован создание нового.")
            await self.create_account()

        page = await self._base_fetch(
            self.CREATE_PAGE_URL,
            PageResponse,
            ParamBuilder.build_page,
            access_token=access_token or self._access_token,
            title=title,
            content=self._create_nodes(content),
            author_name=author_name,
            author_url=author_url,
            return_content=return_content,
            type="json",
            method="post",
        )
        if not page.ok:
            logger.error(f"Не удалось сгенерировать страницу (error={page.error})")
        else:
            logger.success(f"Страница создана (URL={page.result.url})")

        return page

    async def _base_fetch(
        self,
        url: str,
        model: type[_T],
        builder: Callable[[dict], dict],
        *args,
        method: str = "GET",
        type: str = "params",
        **kwargs,
    ):
        response = await self.client.request(
            method=method, url=url, **{type: builder(*args, **kwargs)}
        )
        response.raise_for_status()
        content = response.json()

        if not content["ok"]:
            return ErrorResponse(ok=content["ok"], error=content["error"])

        return model.model_validate(content)

    def _create_nodes(self, content: str, features: str | None = None) -> list[Node]:
        soup = BeautifulSoup(content, features=features or self.features)
        nodes: list[Node] = []

        for child in soup:
            if child.name is None:
                nodes.append(str(child.string))
                continue
            tag = Node(
                tag=child.name,
                attrs=child.attrs,
                children=self._create_nodes("".join(map(str, child.contents))),
            )
            nodes.append(tag)
        return nodes
