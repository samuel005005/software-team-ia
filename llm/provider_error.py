class LLMProviderError(Exception):
    """Error controlado al interactuar con un proveedor LLM."""

    def __init__(self, message: str, provider: str | None = None) -> None:
        self.provider = provider
        super().__init__(message)
