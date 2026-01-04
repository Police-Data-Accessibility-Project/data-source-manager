from pydantic import BaseModel


class URLRootURLMapping(BaseModel):
    url: str
    root_url: str

    @property
    def is_root_url(self) -> bool:
        # Add rstrip to handle trailing slashes
        return self.url.rstrip("/") == self.root_url.rstrip("/")