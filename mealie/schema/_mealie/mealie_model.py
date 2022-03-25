from __future__ import annotations

from typing import TypeVar

from humps.main import camelize
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class MealieModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True

    def cast(self, cls: type[T], **kwargs) -> T:
        """
        Cast the current model to another with additional arguments. Useful for
        transforming DTOs into models that are saved to a database
        """
        create_data = {field: getattr(self, field) for field in self.__fields__ if field in cls.__fields__}
        create_data.update(kwargs or {})
        return cls(**create_data)

    def map_to(self, dest: T) -> T:
        """
        Map matching values from the current model to another model. Model returned
        for method chaining.
        """

        for field in self.__fields__:
            if field in dest.__fields__:
                setattr(dest, field, getattr(self, field))

        return dest

    def map_from(self, src: BaseModel):
        """
        Map matching values from another model to the current model.
        """

        for field in src.__fields__:
            if field in self.__fields__:
                setattr(self, field, getattr(src, field))
