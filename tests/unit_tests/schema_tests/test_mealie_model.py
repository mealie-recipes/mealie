from mealie.schema._mealie.mealie_model import MealieModel


class TestModel(MealieModel):
    long_name: str
    long_int: int
    long_float: float


class TestModel2(MealieModel):
    long_name: str
    long_int: int
    long_float: float
    another_str: str


def test_camelize_variables():
    model = TestModel(long_name="Hello", long_int=1, long_float=1.1)

    as_dict = model.dict(by_alias=True)

    assert as_dict["longName"] == "Hello"
    assert as_dict["longInt"] == 1
    assert as_dict["longFloat"] == 1.1


def test_cast_to():

    model = TestModel(long_name="Hello", long_int=1, long_float=1.1)

    model2 = model.cast(TestModel2, another_str="World")

    assert model2.long_name == "Hello"
    assert model2.long_int == 1
    assert model2.long_float == 1.1
    assert model2.another_str == "World"


def test_map_to():

    model = TestModel(long_name="Model1", long_int=100, long_float=1.5)

    model2 = TestModel2(long_name="Model2", long_int=1, long_float=1.1, another_str="World")

    model.map_to(model2)

    assert model2.long_name == "Model1"
    assert model2.long_int == 100
    assert model2.long_float == 1.5
    assert model2.another_str == "World"


def test_map_from():
    model = TestModel(long_name="Model1", long_int=50, long_float=1.5)

    model2 = TestModel2(long_name="Hello", long_int=1, long_float=1.1, another_str="World")

    model2.map_from(model)

    assert model2.long_name == "Model1"
    assert model2.long_int == 50
    assert model2.long_float == 1.5
    assert model2.another_str == "World"
