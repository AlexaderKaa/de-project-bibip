import os
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class ModelIndex:
    def __init__(self, model_id: int, pos_in_data_file: int):
        self.model_id = model_id
        self.pos_in_data_file = pos_in_data_file


class CarIndex:
    def __init__(self, car_id: str, pos_in_data_file: int):
        self.car_id = car_id
        self.pos_in_data_file = pos_in_data_file


class CarService:
    def _format_path(self, filename: str) -> str:
        return os.path.join(self.root_dir, filename)

    def _read_file(self, filename: str) -> list[list[str]]:
        if not os.path.exists(self._format_path(filename)):
            return []

        with open(self._format_path(filename), "r", encoding="utf-8") as f:
            lines = f.readlines()
            split_lines = [line.strip().split(",") for line in lines]
            return split_lines

    # Задание 1. Сохранение автомобилей и моделей
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.model_index: list[ModelIndex] = []

        split_model_lines = self._read_file("models_index.txt")
        self.model_index = [ModelIndex(int(ml[0]), int(ml[1])) for ml in split_model_lines]

        split_car_lines = self._read_file("cars_index.txt")
        self.car_index = [CarIndex(cl[0], int(cl[1])) for cl in split_car_lines]

    def add_model(self, model: Model) -> Model:
        with open(self._format_path("models.txt"), "a", encoding="utf-8") as f:
            str_model = f"{model.id},{model.name},{model.brand}".ljust(500)
            f.write(str_model + "\n")

        new_mi = ModelIndex(model.id, len(self.model_index))

        self.model_index.append(new_mi)
        self.model_index.sort(key=lambda x: x.model_id)

        with open(self._format_path("model_index.txt"), "w", encoding="utf-8") as f:
            for current_mi in self.model_index:
                str_model = f"{current_mi.model_id},{current_mi.pos_in_data_file}".ljust(50)
                f.write(str_model + "\n")

        return model

    # Задание 1. Сохранение автомобилей и моделей
    def add_car(self, car: Car) -> Car:
        with open(self._format_path("cars.txt"), "a", encoding="utf-8") as f:
            str_car = f"{car.vin},{car.model},{car.price},{car.date_start},{car.status}".ljust(500)
            f.write(str_car + "\n")

        new_ci = CarIndex(car.vin, len(self.car_index))

        self.car_index.append(new_ci)
        self.car_index.sort(key=lambda x: x.car_id)

        with open(self._format_path("car_index.txt"), "w", encoding="utf-8") as f:
            for current_mi in self.car_index:
                str_car = f"{current_mi.car_id},{current_mi.pos_in_data_file}".ljust(50)
                f.write(str_car + "\n")

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        raise NotImplementedError

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        raise NotImplementedError
        # file.seek(501 * position_in_data_file)

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        raise NotImplementedError

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        raise NotImplementedError

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        raise NotImplementedError

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        raise NotImplementedError
