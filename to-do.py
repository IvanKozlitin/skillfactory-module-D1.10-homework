import sys
import requests

base_url = "https://api.trello.com/1/{}"
auth_params = {
    'key': "e3af0fe8e062b2b6ca5f9c906b8dc7fd",
    'token': "08100766b52d1e38c68c2e6002abe277062726959a3126dae5a5dbb579ed2d3a", }
board_id = "y4ohsuNE"


def read():
    # Получим данные всех колонок на доске:
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:
    for column in column_data:
        # Получим данные всех задач в колонке и перечислим все названия
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(column['name'] + " ({})".format(str(len(task_data))))  # Выводим название колонки + количество задач в ней
        i = 1  # счётчик задач в колонке
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t{}: '.format(i) + task['name'] + ", id: {}".format(task["id"]))
            i += 1


def create(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Проверим существует ли такая колонка
    if not column_check(column_name, column_data):
        return print("Колонка с таким именем не найдена, попробуйте изменить имя колонки в запросе")
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
            # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break
    print("Карточка с названием {} успешно добавлена в колонку {}.".format(name, column_name))


def create_col(column_name):
    # Создадим колонку с именем column_name
    board_id_for_request = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
    requests.post(base_url.format('lists'),
                  params={'name': column_name, 'idBoard': board_id_for_request["id"], "pos": "bottom", **auth_params})
    print("Колонка с названием {} успешно добавлена.".format(column_name))


def task_selection(list_tasks, name_task):
    # Интерфес запроса выбора нужной задачи для перемещения в другую колонку, для функции move()
    i = 1  # счётчик задач и id используемый для выбора задачи пользователем
    tasts_dict = {}
    print(
        "Уважаемый пользователь, мы нашли несколько задач с название '{}', пожалуйста веберите какую именно вы хотите "
        "переместить:".format(name_task))
    for task in list_tasks:
        tasts_dict[str(i)] = task
        task_data = requests.get(base_url.format('cards') + '/' + task, params=auth_params).json()
        column_data = requests.get(base_url.format('lists') + '/' + task_data["idList"], params=auth_params).json()
        print("{} - Название задачи: {}, Находится в колонке: {}, её id: {}".format(i, task_data["name"],
                                                                                    column_data["name"],
                                                                                    task_data["id"]))
        i += 1

    result = tasts_dict.get(input("Введите номер задачи (Находится слева от названия), которую хотите переместить: "))

    while result is None:
        print("Вы выбрали номер задачи, которого нет в списке, либо ввели его некорректо, попробуйте снова")
        result = tasts_dict.get(
            input("Введите номер задачи (Находится слева от названия), которую хотите переместить: "))

    return result


def column_check(column_name, column_data):
    list_column = []
    for column in column_data:
        if column['name'] == column_name:
            list_column.append(column['name'])
    return len(list_column) > 0


def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Проверим существует ли такая колонка
    if not column_check(column_name, column_data):
        return print("Колонка с таким именем не найдена, попробуйте изменить имя колонки в запросе")
    list_tasks = []  # Список всех найденных задач с запрошенным именем, сохраняем их id
    # Среди всех колонок нужно найти задачу по имени и получить её id
    task_id = None
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                list_tasks.append(task['id'])

    if len(list_tasks) == 1:
        task_id = list_tasks[0]
    elif len(list_tasks) == 0:
        return print("Задача с таким именем не найдена, попробуйте изменить имя задачи в запросе")
    elif len(list_tasks) >= 2:
        task_id = task_selection(list_tasks, name)  # У нас несколько задач с одинаковым именем, отправляем на выбор

        # Теперь, когда у нас есть id задачи, которую мы хотим переместить
    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + task_id + '/idList',
                         data={'value': column['id'], **auth_params})
            break

    print("Задача с именем '{}' успешно перемещена в колонку '{}'".format(name, column_name))


if __name__ == "__main__":
    if len(sys.argv) == 1:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'create_col':
        create_col(sys.argv[2])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
