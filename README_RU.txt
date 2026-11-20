# Корпус Терна — исправление компиляции 0.10.1

В GitHub Actions, сборка #1 (44784286582), после успешной проверки XML/PNG, dotnet build обнаружил ошибки CS0115:
- ThornWhip/Source/ThornMoats.cs, строка 31
- ThornWhip/Source/TurretRetrofits.cs, строка 56

Обе вызваны попыткой переопределить отсутствующий в сборочных библиотеках RimWorld 1.7 метод ThingComp.PostDeSpawn(Map).

## Установка
1. Открой локальную папку репозитория ThornWhip через GitHub Desktop > Repository > Show in Explorer.
2. Скопируй в неё папку ThornWhip из этого архива (с заменой 2 существующих .cs файлов, без удаления других файлов).
3. Вернись в GitHub Desktop. В Summary укажи: `Fix RimWorld 1.7 compilation CS0115`.
4. Нажми Commit to main, затем Push origin.
5. На GitHub > Actions проверь новую сборку. Если возникнут другие ошибки, прочтём новый лог.

Компиляция этого исправления ещё НЕ проверена. Цель — убрать две подтверждённые ошибки CS0115.
