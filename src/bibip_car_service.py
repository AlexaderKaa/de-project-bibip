"""Carservice Bibip
   pos_in_file = pif
"""

import os
from decimal import Decimal
from datetime import datetime
from collections import Counter
from models import Car, CarFullInfo, CarStatus, Model, ModelSaleStats, Sale


class ModelIndex:
    """ Инициализация класса индексов models """
    def __init__(self, model_id: int, pif_models: int):
        self.model_id = model_id
        self.pif_models = pif_models

class CarIndex:
    """ Инициализация класса индексов cars """
    def __init__(self, car_id: str, pif_cars: int):
        self.car_id = car_id
        self.pif_cars = pif_cars

class SaleIndex:
    """ Инициализация класса индексов sales """
    def __init__(self, car_vin: str, pif_sales: int):
        self.car_vin = car_vin
        self.pif_sales = pif_sales

class CarService:
    """ Класс CarService. 
    Методы для работы с данными автосалона "БиБип".
    1.1 Сохранение моделей, создание индекса по ключевому полю.
    1.2 Сохранение авто, создание индекса по ключевому полю.
    2.1 Сохранение продаж, создание индекса ключевому полю.
    2.2 Изменение статуса авто после продажи.
    3. Список доступных к продаже авто.
    4. Получение детальной информации об авто.
    5. Обновление ключевого поля.
    6. Удаление строки в продажах (отмена).
    7. Список трёх самых продаваемых моделей.
    """
    def _format_path(self, filename: str) -> str:
        """ Объединяем root_directory_path и имя файла для получения полного пути """
        return os.path.join(self.root_dir_path, filename)

    def _r_file(self, filename: str) -> list[list[str]]:
        """ Приватный метод. Чтение файла."""
        if not os.path.exists(self._format_path(filename)):
            return []
        else:
            with open(self._format_path(filename), 'r', encoding='utf-8') as f:
                rows = f.readlines()
                split_rows= [row.strip().split(',') for row in rows]
                return split_rows

    def __init__(self, root_dir_path: str) -> None:
        self.root_dir_path = root_dir_path
        self.model_index: list[ModelIndex] = []
        self.car_index: list[CarIndex] = []
        self.sale_index:list[SaleIndex] = []

        split_rows_mi = self._r_file("models_index.txt")
        self.model_index = [ModelIndex(int(r[0]), int(r[1])) for r in split_rows_mi]

        split_rows_ci = self._r_file('cars_index.txt')
        self.car_index = [CarIndex(str(r[0]), int(r[1])) for r in split_rows_ci]

        split_rows_si = self._r_file('sales_index.txt')
        self.sale_index = [SaleIndex(str(r[0]), int(r[1])) for r in split_rows_si]

    def _rw_file(self, filepath: str, data: list, ljust_par: int) -> None:
        """Приватный метод. Перезапись файла."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                result = ','.join([x for x in item]).ljust(ljust_par) + '\n'
                f.write(result)

    def _get_model_info(self, model_id: str) -> Model:
        """ Получение информации по id модели. """
        # читаем индекс и определяем номер строки в models
        with open(self._format_path('models_index.txt'), 'r', encoding='utf-8') as fmi:
            for row_mi in fmi:
                mod_id, row_mi_rnum = row_mi.strip().split(',')
                if mod_id == model_id:
                    target_row = int(row_mi_rnum) # искомая строка в models
                    break
            else:
                raise ValueError('ID модели снет найден в продажах')

        with open(self._format_path('models.txt'), 'r', encoding='utf-8') as fm:
            fm.seek(target_row * 502)
            row_model = fm.readline().strip().split(',')

        return Model(id=row_model[0], name=row_model[1], brand=row_model[2])

    # Задание 1.1 Сохранение моделей авто, создание индексов.
    def add_model(self, model: Model) -> Model:
        """ Сохранение моделей авто, создание индексов. """
        # открываем файл  models на добавление строк и формируем строки из атрибутов класса Model
        with open(self._format_path('models.txt'), 'a', encoding="utf-8") as fm:
            str_model = f'{model.id},{model.name},{model.brand}'.ljust(500) + '\n'
            fm.write(str_model)

        # Создаем экемпляр сласса ModelIndex
        new_mi = ModelIndex(model.id, len(self.model_index))
        self.model_index.append(new_mi)
        self.model_index.sort(key=lambda x: x.model_id)

        # Создание файла с индексами, отсортированными по ключевому полю
        self._rw_file(self._format_path('models_index.txt'),
                        data=[[str(current_mi.model_id), str(current_mi.pif_models)]
                              for current_mi in self.model_index],
                        ljust_par=50)

        return model

    # Задание 1.2 Сохранение авто, создание индексов.
    def add_car(self, car: Car) -> Car:
        """ Сохранение авто, создание индексов. """
        with open(self._format_path("cars.txt"), "a", encoding="utf-8") as fc:
            str_cars = f'{car.vin},{car.model},{car.price},{car.date_start},{car.status}'.ljust(500) + '\n'
            fc.write(str_cars)

        # Создаем экемпляр сласса CarIndex
        new_ci = CarIndex(car.vin, len(self.car_index))
        self.car_index.append(new_ci)
        self.car_index.sort(key=lambda x: x.car_id)

        # Создание файла с индексами cars_index по ключевому полю car_id - VIN
        self._rw_file(self._format_path('cars_index.txt'),
                         data=[[str(current_ci.car_id),
                                str(current_ci.pif_cars)] for current_ci in self.car_index],
                         ljust_par=50)

        return car

    # Задание 2. Сохранение продаж.
    def sell_car(self, sale: Sale) -> Car:
        """ Сохранение продажи, изменения статуса авто в cars. """
        with open(self._format_path('sales.txt'), 'a', encoding='utf-8') as fs:
            str_sales = f'{sale.sales_number},{sale.car_vin},{sale.sales_date},{sale.cost}'.ljust(500) + '\n'
            fs.write(str_sales)

        # Создаем экемпляр сласса SaleIndex
        new_si = SaleIndex(car_vin=sale.car_vin, pif_sales=len(self.sale_index))
        self.sale_index.append(new_si)
        self.sale_index.sort(key=lambda x: x.car_vin)

        # Создание файла с индексами sales_index по ключевому полю VIN
        self._rw_file(self._format_path('sales_index.txt'),
                         data=[[str(current_si.car_vin),
                                str(current_si.pif_sales)] for current_si in self.sale_index],
                         ljust_par=50)

        # Номер строки в индексе по VIN
        rows_ci = self._r_file(self._format_path('cars_index.txt'))
        target_row_ci = -1
        for row_ci in rows_ci:
            car_id, row_ci_rnum = row_ci[0], row_ci[1]
            if car_id == sale.car_vin:
                target_row_ci = int(row_ci_rnum)
                break
        if target_row_ci == -1:
            raise ValueError(f'Авто с VIN-кодом "{sale.car_vin}" не найден')

        # Обновляем статус в cars, что авто продан
        with open(self._format_path('cars.txt'), 'r+', encoding='utf-8') as fc:
            fc.seek(target_row_ci * 502)
            rows_cars = fc.readline()
            row_car = rows_cars.strip().split(',')
            car = Car(
                vin=str(row_car[0]),
                model=int(row_car[1]),
                price = Decimal(row_car[2]),
                date_start = datetime.strptime(row_car[3], "%Y-%m-%d %H:%M:%S"),
                status=CarStatus(row_car[4])
                )
            car.status = CarStatus.sold
            fc.seek(target_row_ci * 502)
            row_car_upd = f'{car.vin},{car.model},{car.price},{car.date_start},{car.status}'.ljust(500) + '\n'
            fc.write(row_car_upd)

        return car

    # Задание 3. Доступные к продаже
    def get_cars(self, status: CarStatus) -> list[Car]:
        """ Определение списка доступных к продаже авто """
        cars = []
        rows_cars = self._r_file(self._format_path('cars.txt'))
        for row_car in rows_cars:
            if row_car[4] == status:
                car = Car(
                          vin=row_car[0],
                          model=int(row_car[1]),
                          price=Decimal(row_car[2]),
                          date_start=datetime.strptime(row_car[3], '%Y-%m-%d %H:%M:%S'),
                          status=CarStatus(row_car[4])
                          )
                cars.append(car)
        # Сортировка по VIN
        #cars = sorted(cars, key=lambda car: car.vin)
        return cars

    # Задание 4. Детальная информация
    def get_car_info(self, vin: str) -> CarFullInfo | None:
        """ Получение детальной информации об авто. """
        rows_ci = self._r_file(self._format_path('cars_index.txt'))
        # Номер строки в индексе по VIN
        target_row_ci = -1
        for row_ci in rows_ci:
            row_ci_car_vin, row_ci_rnum = row_ci[0], row_ci[1]
            if row_ci_car_vin == vin:
                target_row_ci = int(row_ci_rnum)
                break
        if target_row_ci == -1:
            return None
        #raise ValueError(f'Авто с VIN-кодом "{vin}" не найден')
        #print(f'Test: {target_row_ci}, Type of target_row_ci: {type(target_row_ci)}')

        # Получение данных об авто
        with open(self._format_path('cars.txt'), 'r', encoding='utf-8') as fc:
            fc.seek(target_row_ci * 502)
            rows_cars = fc.readline()
            row_car = rows_cars.strip().split(',')
        # Получаем id модели, чтобы связать с models
        model_id = int(row_car[1])

        # Читаем индекс для определения из models по model_id
        rows_mi = self._r_file(self._format_path('models_index.txt'))
        target_row_mi = -1
        for row_mi in rows_mi:
            row_mi_id, row_mi_rnum = row_mi[0], row_mi[1]
            if model_id == int(row_mi_id):
                target_row_mi = int(row_mi_rnum)
                break
        if target_row_mi == -1:
            return None
            #raise ValueError('Модель с VIN-кодом "{vin}" не найдена')

        with open(self._format_path('models.txt'), 'r', encoding='utf-8') as fm:
            fm.seek(target_row_mi * 502)
            rows_models = fm.readline()
            row_model = rows_models.strip().split(',')

        # Проверка продажи авто
        if  str(row_car[4]) != CarStatus.sold:
            s_date = None
            s_cost = None
        else:
            # Ищем по индексу продажу
            rows_si = self._r_file(self._format_path('sales_index.txt'))
            target_row_si = -1
            for row_si in rows_si:
                row_si_car_vin, row_si_rnum = row_si[0],row_si[1]
                if row_si_car_vin == vin:
                    target_row_si = int(row_si_rnum)
                    break
            if target_row_si == -1:
                raise ValueError(f'Авто с VIN-кодом "{vin}" не найден')

            # Собираем информацию о продаже авто
            with open(self._format_path('sales.txt'), 'r', encoding='utf-8') as fs:
                fs.seek(target_row_si * 502)
                rows_sales = fs.readline()
                row_sales = rows_sales.strip().split(',')
                s_date = datetime.strptime(row_sales[2], "%Y-%m-%d %H:%M:%S")
                s_cost =Decimal(row_sales[3])

        return CarFullInfo(
            vin= str(row_car[0]),
            car_model_name= str(row_model[1]),
            car_model_brand= str(row_model[2]),
            price= Decimal(row_car[2]),
            date_start= datetime.strptime(row_car[3], "%Y-%m-%d %H:%M:%S"),
            status= CarStatus(row_car[4]),
            sales_date= s_date,
            sales_cost= s_cost
        )

    # Задание 5. Обновление ключевого поля
    def update_vin(self, vin: str, new_vin: str) -> Car:
        """ Обновление ключевого поля car_vin. """
        rows_ci = self._r_file(self._format_path('cars_index.txt'))
        # Номер строки в индексе по VIN
        target_row_ci = -1
        for row_ci in rows_ci:
            car_id, row_ci_num = row_ci[0], row_ci[1]
            if car_id == vin:
                target_row_ci = int(row_ci_num)
                break
        if target_row_ci == -1:
            #return None
            raise ValueError(f'Авто с VIN-кодом "{vin}" не найдено')
        #print(target_row_ci)

        # Получаем данные об авто (с возможностью перезаписи)
        with open(self._format_path('cars.txt'), 'r+', encoding='utf-8') as fc:
            fc.seek(target_row_ci * 502)
            rows_cars = fc.readline()
            row_car = rows_cars.strip().split(',')
            # Обновляем ключ = VIN
            row_car[0] = new_vin

            # перезаписываем строку в cars
            fc.seek(target_row_ci * 502)
            row_car_upd = ','.join(row_car).ljust(500) + '\n'
            fc.write(row_car_upd)

        # Обновляем и сортируем индекс (car_id = VIN)
        for ci in self.car_index:
            if ci.car_id == vin:
                ci.car_id = new_vin

        self.car_index.sort(key=lambda x: x.car_id)

        # Перезаписываем файл с индексами cars_index по ключевому полю car_id - VIN
        self._rw_file(self._format_path('cars_index.txt'),
                         data=[[str(current_ci.car_id),
                                str(current_ci.pif_cars)] for current_ci in self.car_index],
                         ljust_par=50)

        car = Car(
            vin=new_vin,
            model=int(row_car[1]),
            price=Decimal(row_car[2]),
            date_start=datetime.strptime(row_car[3], "%Y-%m-%d %H:%M:%S"),
            status=CarStatus(row_car[4])
            )

        return car

    # Задание 6. Удаление продажи
    def revert_sale(self, sales_number: str) -> Car:
        """ Отмена продажи авто. """
        # 1. Читаем файл продаж, чтобы найти vin и номер строки на удаление
        vin = None

        target_row_del = -1
        with open(self._format_path('sales.txt'), 'r', encoding='utf-8') as fsd:
            rows_sales = fsd.readlines()  # Читаем строки сразу
            for line_number, line in enumerate(rows_sales):
                sales_num, car_vin, _, _ = line.strip().split(',')
                if sales_num == sales_number:
                    vin = car_vin
                    target_row_del = line_number  # Сохраняем номер строки
                    break
        if target_row_del == -1:
            raise ValueError(f'Авто с VIN-кодом "{vin}" не продан')

        # 2. Обновляем статус авто. Ищем по индексу.
        rows_ci = self._r_file(self._format_path('cars_index.txt'))
        # Номер строки в индексе по VIN
        row_ci = -1
        for row_ci in rows_ci:
            car_id, row_ci_num = row_ci[0], row_ci[1]
            if car_id == vin:
                row_ci = int(row_ci_num)
                break
        if row_ci == -1:
            #return None
            raise ValueError(f'Авто с VIN-кодом "{vin}" не найден')

        # Обновляем статус для авто и перезаписываем строку в файле cars
        with open(self._format_path('cars.txt'), 'r+', encoding='utf-8') as fc:
            fc.seek(row_ci * 502)
            rows_cars = fc.readline()
            row_car = rows_cars.strip().split(',')

            car = Car(
                vin=str(row_car[0]),
                model=int(row_car[1]),
                price=Decimal(row_car[2]),
                date_start=datetime.strptime(row_car[3], "%Y-%m-%d %H:%M:%S"),
                status=CarStatus(row_car[4])
            )

            car.status = CarStatus.available
            row_car_upd = f'{car.vin},{car.model},{car.price},{car.date_start},{car.status}'.ljust(500) + '\n'
            fc.seek(row_ci * 502)
            fc.write(row_car_upd)

        # Удаляем запись из продаж
        with open(self._format_path('sales.txt'), 'w', encoding='utf-8') as fsd:
            for row_sale_rnum, row_sale in enumerate(rows_sales):
                if row_sale_rnum != target_row_del:  # Пропускаем строку с удаляемой продажей
                    fsd.write(row_sale)

        # Считываем продажи, чтобы перезаписать отсортированный индекс
        with open(self._format_path('sales.txt'), 'r', encoding='utf-8') as fsd:
            sale_lines = fsd.readlines()

        new_sales_index = []

        for row_sale_rnum, row_sale in enumerate(sale_lines):
            _, car_vin, _, _ = row_sale.strip().split(',')
            new_sales_index.append((car_vin, row_sale_rnum))

        new_sales_index.sort(key=lambda x: x[0])

        #self._rw_file(self._format_path('sales_index.txt'), data=[new_sales_index], ljust_par=50)
        with open(self._format_path('sales_index.txt'), 'w', encoding='utf-8') as fsi:
            for car_vin, row_sale_rnum in new_sales_index:
                fsi.write(f'{car_vin},{row_sale_rnum}'.ljust(50) +'\n')

        return car

    # Задание 7. Самые продаваемые модели
    def top_models_by_sales(self) -> list[ModelSaleStats]:
        """ ТОП-3 самых продаваемых моделей. """
        # Поиск авто по vin и формирование списка
        with open(self._format_path('sales_index.txt'), 'r', encoding='utf-8') as fs:
            rows_sales:list[str] = fs.readlines()
        car_vin_list = []
        for s_line in rows_sales:
            car_vin, _ = s_line.strip().split(',')
            car_vin_list.append(car_vin)

        model_id_list = []
        for item in car_vin_list:
            with open(self._format_path('cars_index.txt'), 'r', encoding='utf-8') as fci:
                index_lines: list[str] = fci.readlines()
                target_string = -1
                for ci_line in index_lines:
                    car_vin, line_number = ci_line.strip().split(',')
                    if car_vin == item:
                        target_string = int(line_number)
                        break
            with open(self._format_path('cars.txt'), 'r+', encoding='utf-8') as fc:
                fc.seek(target_string * 502)
                rows_cars = fc.readline()
                row_car = rows_cars.strip().split(',')
                model_id_list.append(row_car[1])

        # ТОП-3 модели по количеству продаж. Записываем в ModelSaleStats
        top_models = dict(Counter(model_id_list))
        top_3_models = sorted(top_models.items(), key=lambda x: x[1], reverse=True)[:3]

        res_top_3 = []
        for model_id, sales_number in top_3_models:
            model_info = self._get_model_info(model_id)
            res_top_3.append(ModelSaleStats(car_model_name=str(model_info.name),
                                        brand=model_info.brand,
                                        sales_number=sales_number))

        return res_top_3
