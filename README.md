# Blender Unity Mesh Menu

Небольшой аддон для Blender, который добавляет отдельное меню Unity Mesh в Shift + A и создает примитивы сразу в размерах, удобных для Unity (по умолчанию 1 метр).

<img width="412" height="274" alt="изображение" src="https://github.com/user-attachments/assets/610be479-e978-461e-8f7c-348ec0081608" />



Аддон также умеет (опционально) переопределять Shift + D в Object Mode, чтобы дубликаты получали имена в стиле Cube_001 вместо Cube.001.

<img width="604" height="280" alt="изображение" src="https://github.com/user-attachments/assets/a9ab1b44-ca1b-40ec-beb7-91b65fb0548a" />


Важно: стиль имен с нижним подчеркиванием сделан под мои личные предпочтения. Используйте только если вас устраивает такой нейминг. Если не любите underscore, просто отключите опции дублирования в настройках аддона.

## Возможности

- Отдельный пункт Unity Mesh в меню Add (Shift + A)
- Примитивы создаются сразу нужного размера (Default Size, по умолчанию 1.0m)
- Имена новых объектов в стиле:
  - Cube, Cube_001, Cube_002 ...
  - Plane, Plane_001 ...
- Опционально:
  - Shift + D в Object Mode вызывает Unity Duplicate
  - стандартный Duplicate Objects (Shift + D) можно отключить из аддона, чтобы не было конфликта
- Переименовывает также Mesh Data, но только если data не шарится (users == 1), чтобы не ломать shared data

## Требования

- Blender 4.0+ (тестировалось на Blender 5.0.x)

## Установка (Blender 5.0 и выше)

Рекомендуемый способ: установка через Preferences, кнопкой Install from Disk.

1. Скачайте файл аддона `AbyssMothUnityPrimitives.py` в любую папку (например Downloads)
2. Blender -> Edit -> Preferences -> Add-ons
3. Нажмите кнопку меню справа сверху и выберите Install from Disk
4. Укажите скачанный `AbyssMothUnityPrimitives.py`
5. В списке аддонов включите галочку у "AbyssMoth Unity-friendly Primitives"

Blender сам скопирует файл куда нужно и создаст папки, если их не было.

Важно:
- Не кладите файл вручную в папку `.../scripts/addons/` перед установкой через Install from Disk
- Если файл уже лежит внутри пути аддонов, Blender может ругаться, что источник находится внутри пути поиска аддонов

<img width="268" height="296" alt="изображение" src="https://github.com/user-attachments/assets/bfe16f69-7001-4f15-a4fb-3e8044a089ee" />
<img width="498" height="280" alt="изображение" src="https://github.com/user-attachments/assets/5f24c593-1656-4f88-a4dc-60de898f4482" />
<img width="717" height="284" alt="изображение" src="https://github.com/user-attachments/assets/220ed690-9b32-4c18-ab2f-484386435b91" />


## Использование

1. Откройте 3D View
2. Нажмите Shift + A (Английская раскладка!!!)
3. Выберите Unity Mesh
4. Создайте примитив

Доступные примитивы:
- Cube
- Plane
- Grid
- UV Sphere
- Ico Sphere
- Cylinder
- Cone

## Настройки аддона

Edit -> Preferences -> Add-ons -> AbyssMoth Unity-friendly Primitives

- Default Size (meters)
  - Базовый размер примитивов, по умолчанию 1.0
- Bind Unity Duplicate to Shift+D (Object Mode)
  - Включает Unity Duplicate на Shift + D
- Disable default Duplicate Objects (Shift+D)
  - Отключает стандартный Duplicate Objects на Shift + D, чтобы не было конфликтов

Если хотите только меню и создание 1m примитивов, но не хотите менять поведение Shift + D:
- выключите Bind Unity Duplicate to Shift+D
- выключите Disable default Duplicate Objects

<img width="890" height="392" alt="изображение" src="https://github.com/user-attachments/assets/ca5bbc07-1dfa-4176-aee9-501d75f2e231" />


## Про русский "Куб" и локализацию

Если у вас новые объекты создаются как "Куб", "Цилиндр" и т.д., это настройка Blender:
Preferences -> Interface -> Translation
Снимите галочку New Data, если хотите, чтобы имена объектов были на английском.
Tooltips можно оставить включенными.

<img width="890" height="508" alt="изображение" src="https://github.com/user-attachments/assets/8426194a-81a3-4ff6-8d1c-d72a7b0d0b30" />


## Экспорт в Unity

Аддон не заменяет экспорт, он только помогает со сценой и размерами.

Рекомендации:
- Scene Units: Metric
- Unit Scale: 1.0
- В Unity 1 unit = 1 meter, поэтому Default Size = 1.0 дает куб 1x1x1 как в Unity

Экспорт FBX (типичный вариант):
- File -> Export -> FBX
- Apply Transform: включить при необходимости
- Forward, Up: под ваш пайплайн (часто -Z Forward, Y Up)

Экспорт glTF:
- File -> Export -> glTF 2.0
- Удобно для простых моделей и материалов

## Ограничения и предупреждения

- Нейминг с нижним подчеркиванием намеренно жесткий и может не понравиться тем, кто привык к стандартному стилю Blender с .001
- Переопределение Shift + D влияет только на Object Mode
- Если вы активно используете свои кастомные keymap, проверьте, что Shift + D не занят другими действиями

## Удаление

1. Preferences -> Add-ons -> выключите аддон
2. Удалите аддон через интерфейс Blender или удалите файл аддона из user scripts/addons (если вы знаете где он лежит)
3. Перезапустите Blender

<img width="694" height="401" alt="изображение" src="https://github.com/user-attachments/assets/c577780d-6506-443f-85a3-e3339799d86d" />
