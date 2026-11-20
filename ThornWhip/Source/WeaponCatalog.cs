using System;

namespace ThornWhip
{
    // Source-generated catalog. Never reorder options 0/1; saved blueprints use integer indices.
    public sealed class ModuleOption
    {
        public readonly string Name;
        public readonly float Sights, Spread, Sway, Cooldown, Mass, Bulk, Value;
        public readonly float Recoil, Warmup, Reload, Range, NightVision;
        public readonly int Steel, Industrial, Advanced, Gold;
        public ModuleOption(string name, float sights=0, float spread=0, float sway=0,
            float cooldown=0, float mass=0, float bulk=0, float value=0,
            float recoil=0, float warmup=0, float reload=0, float range=0,
            float nightVision=0, int steel=0, int industrial=0, int advanced=0, int gold=0)
        {
            Name=name; Sights=sights; Spread=spread; Sway=sway; Cooldown=cooldown;
            Mass=mass; Bulk=bulk; Value=value; Recoil=recoil; Warmup=warmup;
            Reload=reload; Range=range; NightVision=nightVision;
            Steel=steel; Industrial=industrial; Advanced=advanced; Gold=gold;
        }
    }
    public sealed class ModuleSlot
    {
        public readonly string Label; public readonly bool Required;
        public readonly ModuleOption[] Options;
        public ModuleSlot(string label, bool required, params ModuleOption[] options) { Label=label; Required=required; Options=options; }
    }
    public sealed class SpecialModule
    {
        public readonly string Target, Name, Details;
        public readonly ModuleOption Effects;
        public SpecialModule(string target, string name, string details, ModuleOption effects)
        { Target=target; Name=name; Details=details; Effects=effects; }
    }
    public sealed class WeaponFamily
    {
        public readonly string Key, Label, Caliber;
        public readonly float Sights, Spread, Sway, Cooldown, Mass, Bulk, MarketValue;
        public readonly int[] Magazine, Burst, Ranges;
        public WeaponFamily(string key, string label, string caliber, float sights, float spread, float sway,
            float cooldown, float mass, float bulk, float marketValue, int mag0, int mag1,
            int burst0, int burst1, int range0, int range1)
        { Key=key; Label=label; Caliber=caliber; Sights=sights; Spread=spread; Sway=sway;
          Cooldown=cooldown; Mass=mass; Bulk=bulk; MarketValue=marketValue; Magazine=new[]{mag0,mag1};
          Burst=new[]{burst0,burst1}; Ranges=new[]{range0,range1}; }
    }
    public static class WeaponCatalog
    {
        public static readonly WeaponFamily[] Families = {
            new WeaponFamily("Rifle", "Марксанская винтовка «Плеть Терна»", "5,56×45 NATO", 0.85f, 0.09f, 1.45f, 0.88f, 3.7f, 4.8f, 420f, 20, 30, 2, 1, 55, 70),
            new WeaponFamily("Auto", "Автомат «Гнев Терна»", "5,56×45 NATO", 0.92f, 0.135f, 1.21f, 0.4f, 3.25f, 4.3f, 455f, 25, 40, 5, 3, 40, 51),
            new WeaponFamily("Pistol", "Пистолет «Клык Терна»", "9×19 Parabellum", 0.7f, 0.18f, 0.87f, 0.39f, 1.15f, 1.9f, 260f, 12, 20, 1, 3, 17, 23),
            new WeaponFamily("Launcher", "Гранатомёт «Гром Терна»", "40×46 mm LV", 1.1f, 0.18f, 1.31f, 0.62f, 5.3f, 5.65f, 850f, 3, 6, 1, 2, 34, 40),
        };
        private static readonly ModuleSlot[][] Slots = {
            new ModuleSlot[] {
                new ModuleSlot("Верхняя ствольная коробка",true,
                    new ModuleOption("Двухимпульсная автоматика", sway: 0.045f, cooldown: -0.03f, mass: -0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Одиночный точный цикл", sights: 0.09f, spread: -0.004f, cooldown: 0.03f, mass: 0.11f, recoil: -0.06f, steel: 3, industrial: 1),
                    new ModuleOption("Экономичный кулачковый затвор", cooldown: -0.07f, mass: -0.11f, value: 9f, recoil: 0.15f, steel: 1, industrial: 1),
                    new ModuleOption("Адаптивный сервозатвор", cooldown: -0.025f, mass: 0.19f, value: 52f, recoil: -0.11f, warmup: 0.025f, steel: 4, industrial: 1),
                    new ModuleOption("Нейропрограммируемая автоматика", sights: 0.08f, cooldown: -0.065f, mass: 0.2f, value: 146f, recoil: -0.045f, warmup: -0.025f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Нижняя ствольная коробка",true,
                    new ModuleOption("Стандартная", sway: 0.045f, mass: -0.13f, bulk: -0.1f, steel: 3),
                    new ModuleOption("Нейрокомпозитная", sights: 0.04f, spread: -0.003f, mass: 0.1f, bulk: 0.05f, value: 36f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Штампованная коробка", spread: 0.006f, mass: -0.22f, bulk: -0.12f, value: 12f, steel: 2),
                    new ModuleOption("Керамическая силовая коробка", spread: -0.006f, mass: 0.16f, bulk: 0.09f, value: 63f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Живая метаматериальная коробка", sights: 0.07f, spread: -0.003f, mass: -0.03f, bulk: 0.06f, value: 163f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Ствол",true,
                    new ModuleOption("Короткий", spread: 0.01f, sway: -0.04f, cooldown: -0.03f, mass: -0.18f, bulk: -0.14f, steel: 4),
                    new ModuleOption("Удлинённый", spread: -0.01f, sway: 0.04f, mass: 0.28f, bulk: 0.19f, value: 30f, steel: 5, industrial: 1),
                    new ModuleOption("Карабинный тонкий ствол", spread: 0.017f, mass: -0.27f, bulk: -0.2f, value: 15f, range: -0.07f, steel: 3),
                    new ModuleOption("Матчевый толстостенный ствол", spread: -0.012f, sway: 0.06f, mass: 0.43f, bulk: 0.24f, value: 74f, range: 0.09f, steel: 6, industrial: 1),
                    new ModuleOption("Активно охлаждаемый наноствол", spread: -0.018f, mass: 0.13f, bulk: 0.11f, value: 180f, range: 0.12f, steel: 4, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Затворная группа",true,
                    new ModuleOption("Усиленная", cooldown: -0.04f, mass: -0.08f, recoil: 0.075f, steel: 2, industrial: 1),
                    new ModuleOption("Облегчённая", cooldown: 0.04f, mass: 0.16f, value: 25f, recoil: -0.1f, steel: 6, industrial: 2),
                    new ModuleOption("Простой полусвободный затвор", cooldown: -0.06f, mass: -0.07f, value: 18f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Титановая затворная группа", cooldown: -0.04f, mass: 0.13f, value: 85f, recoil: -0.075f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Электромагнитный затвор", cooldown: -0.075f, mass: 0.18f, value: 197f, recoil: -0.035f, reload: -0.055f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Газовый блок",true,
                    new ModuleOption("Фиксированный", cooldown: -0.03f, mass: -0.07f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Регулируемый", cooldown: 0.025f, mass: 0.11f, value: 38f, recoil: -0.08f, steel: 3, industrial: 1),
                    new ModuleOption("Газовый кран полевого ремонта", cooldown: -0.04f, mass: -0.06f, value: 21f, recoil: 0.095f, steel: 2, industrial: 1),
                    new ModuleOption("Импульсный газовый блок", cooldown: 0.025f, mass: 0.14f, value: 96f, recoil: -0.11f, steel: 8, industrial: 1),
                    new ModuleOption("Автонастраиваемый плазмоклапан", spread: -0.004f, cooldown: -0.02f, mass: 0.17f, value: 214f, recoil: -0.065f, steel: 3, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Ударно-спусковой механизм",true,
                    new ModuleOption("Военный", spread: 0.004f, mass: -0.02f, warmup: -0.04f, steel: 4),
                    new ModuleOption("Прецизионный", sights: 0.07f, spread: -0.008f, value: 36f, warmup: 0.015f, steel: 4, industrial: 2),
                    new ModuleOption("Полевой механический спуск", spread: 0.012f, value: 24f, warmup: -0.055f, steel: 3),
                    new ModuleOption("Двухступенчатый спуск", sights: 0.025f, spread: -0.009f, value: 107f, warmup: 0.015f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Нейросенсорный спуск", sights: 0.12f, spread: -0.003f, value: 231f, warmup: -0.095f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Возвратный механизм",true,
                    new ModuleOption("Усиленная пружина", cooldown: -0.045f, recoil: 0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Инерционный демпфер", cooldown: 0.05f, mass: 0.15f, value: 30f, recoil: -0.12f, steel: 5, industrial: 1),
                    new ModuleOption("Лёгкий буфер", cooldown: -0.08f, mass: -0.07f, value: 27f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Гидравлический буфер", cooldown: 0.025f, mass: 0.24f, value: 118f, recoil: -0.15f, steel: 5, industrial: 1),
                    new ModuleOption("Магнитореологический демпфер", cooldown: -0.03f, mass: 0.21f, value: 248f, recoil: -0.14f, steel: 2, industrial: 1, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Приклад",true,
                    new ModuleOption("Складной", sway: 0.1f, mass: -0.23f, bulk: -0.28f, steel: 3),
                    new ModuleOption("Стабилизированный", sway: -0.09f, mass: 0.22f, bulk: 0.22f, value: 29f, recoil: -0.07f, steel: 6, industrial: 2),
                    new ModuleOption("Каркасный приклад", sway: 0.15f, mass: -0.25f, bulk: -0.35f, value: 30f, steel: 2),
                    new ModuleOption("Матчевый тяжёлый приклад", sway: -0.13f, mass: 0.35f, bulk: 0.3f, value: 129f, recoil: -0.065f, steel: 6, industrial: 2, advanced: 1),
                    new ModuleOption("Гироскопический приклад", sway: -0.115f, mass: 0.23f, bulk: 0.08f, value: 265f, recoil: -0.13f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Цевьё",true,
                    new ModuleOption("Лёгкое", spread: 0.006f, cooldown: -0.02f, mass: -0.2f, steel: 4),
                    new ModuleOption("Охлаждаемое", spread: -0.008f, sway: -0.07f, mass: 0.24f, value: 40f, steel: 3, industrial: 1),
                    new ModuleOption("Перфорированное цевьё", spread: 0.007f, mass: -0.23f, bulk: -0.12f, value: 33f, steel: 3, industrial: 1),
                    new ModuleOption("Углеродный тепловой кожух", spread: -0.01f, sway: -0.06f, mass: 0.27f, value: 57f, steel: 7, industrial: 1),
                    new ModuleOption("Криоканальное цевьё", spread: -0.012f, sway: -0.045f, cooldown: -0.035f, mass: 0.2f, value: 282f, steel: 4, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Магазин",true,
                    new ModuleOption("20 патронов", mass: -0.07f, bulk: -0.07f, reload: -0.07f, steel: 2, industrial: 1),
                    new ModuleOption("30 патронов", mass: 0.17f, bulk: 0.18f, value: 30f, reload: 0.1f, steel: 4, industrial: 2),
                    new ModuleOption("Скоросъёмный магазин", mass: -0.08f, bulk: -0.09f, value: 36f, reload: -0.16f, steel: 1),
                    new ModuleOption("Усиленный магазин", mass: 0.26f, bulk: 0.24f, value: 68f, reload: 0.16f, steel: 8, industrial: 2, advanced: 1),
                    new ModuleOption("Смарт-магазин с диагностикой", cooldown: -0.012f, mass: 0.11f, bulk: 0.06f, value: 299f, reload: -0.1f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Прицельная система",false,
                    new ModuleOption("Механическая", sights: -0.05f, mass: -0.05f, steel: 3),
                    new ModuleOption("Цифровая", sights: 0.22f, mass: 0.13f, value: 66f, warmup: -0.075f, nightVision: 0.1f, steel: 5, industrial: 1, advanced: 1),
                    new ModuleOption("Открытые резервные прицельные", sights: -0.025f, mass: -0.07f, value: 39f, warmup: -0.035f, steel: 2),
                    new ModuleOption("Оптика переменной кратности", sights: 0.28f, mass: 0.28f, value: 79f, warmup: 0.055f, steel: 4, industrial: 1),
                    new ModuleOption("Нейрооптический модуль", sights: 0.2f, mass: 0.16f, value: 159f, warmup: -0.12f, nightVision: 0.18f, steel: 3, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Пистолетная рукоять",true,
                    new ModuleOption("Полимерная", sway: 0.03f, mass: -0.07f, steel: 4),
                    new ModuleOption("Сенсорная", sway: -0.05f, mass: 0.055f, value: 26f, recoil: -0.04f, steel: 6, industrial: 2),
                    new ModuleOption("Петлевая полевая рукоять", sway: 0.05f, mass: -0.09f, value: 11f, steel: 3),
                    new ModuleOption("Биомеханическая рукоять", sway: -0.11f, mass: 0.11f, value: 90f, recoil: -0.03f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Адаптивная сенсорная рукоять", sway: -0.12f, mass: 0.07f, value: 176f, warmup: -0.045f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Рукоятка взвода",true,
                    new ModuleOption("Ручная", cooldown: 0.01f, reload: -0.03f, steel: 2, industrial: 1),
                    new ModuleOption("Электроассистент", mass: 0.09f, value: 30f, reload: -0.12f, steel: 3, industrial: 1, advanced: 1),
                    new ModuleOption("Двусторонняя рукоятка взвода", mass: 0.02f, value: 14f, reload: -0.06f, steel: 1, industrial: 1),
                    new ModuleOption("Сервовзвод", mass: 0.17f, bulk: 0.065f, value: 101f, reload: -0.17f, steel: 6, industrial: 1),
                    new ModuleOption("Бесконтактный привод затвора", cooldown: -0.04f, mass: 0.085f, value: 193f, reload: -0.11f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Дульное устройство",false,
                    new ModuleOption("Пламегаситель", mass: -0.05f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Умный компенсатор", spread: -0.006f, mass: 0.16f, bulk: 0.06f, value: 34f, recoil: -0.12f, steel: 4, industrial: 2),
                    new ModuleOption("Простой дульный тормоз", mass: 0.05f, bulk: 0.035f, value: 17f, recoil: -0.035f, steel: 2),
                    new ModuleOption("Многокамерный компенсатор", mass: 0.18f, bulk: 0.1f, value: 112f, recoil: -0.19f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Активная антиимпульсная насадка", spread: -0.005f, mass: 0.14f, value: 210f, recoil: -0.12f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Нижняя аксессуарная планка",false,
                    new ModuleOption("Базовая нижняя планка", mass: 0.04f, bulk: 0.04f, steel: 3),
                    new ModuleOption("Облегчённая рельса", sway: 0.02f, mass: -0.08f, steel: 2, industrial: 1),
                    new ModuleOption("Усиленная рельса", sway: -0.04f, mass: 0.2f, recoil: -0.02f, steel: 4, industrial: 2),
                    new ModuleOption("Многопозиционный кронштейн", sights: 0.04f, mass: 0.16f, warmup: -0.015f, steel: 3, industrial: 2, advanced: 1),
                    new ModuleOption("Умная интерфейсная рельса", sights: 0.07f, mass: 0.1f, value: 140f, nightVision: 0.03f, steel: 2, industrial: 1, advanced: 3, gold: 5)
                ),
            },
            new ModuleSlot[] {
                new ModuleSlot("Ствольная коробка",true,
                    new ModuleOption("Скорострельный цикл", sway: 0.045f, cooldown: -0.0255f, mass: -0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Контролируемые очереди", sights: 0.09f, spread: -0.004f, cooldown: 0.0255f, mass: 0.11f, recoil: -0.06f, steel: 3, industrial: 1),
                    new ModuleOption("Бюджетный открытый цикл", cooldown: -0.07f, mass: -0.1012f, value: 9f, recoil: 0.15f, steel: 1, industrial: 1),
                    new ModuleOption("Контроллер коротких очередей", cooldown: -0.025f, mass: 0.1748f, value: 52f, recoil: -0.11f, warmup: 0.025f, steel: 4, industrial: 1),
                    new ModuleOption("Предиктивный контроллер огня", sights: 0.08f, cooldown: -0.065f, mass: 0.184f, value: 146f, recoil: -0.045f, warmup: -0.025f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Нижний корпус",true,
                    new ModuleOption("Лёгкий полимер", sway: 0.045f, mass: -0.13f, bulk: -0.1f, steel: 3),
                    new ModuleOption("Экзосплавный", sights: 0.04f, spread: -0.003f, mass: 0.1f, bulk: 0.05f, value: 36f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Штампованный нижний корпус", spread: 0.006f, mass: -0.2024f, bulk: -0.1104f, value: 12f, steel: 2),
                    new ModuleOption("Титановая силовая рама", spread: -0.006f, mass: 0.1472f, bulk: 0.0828f, value: 63f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Плетёный метакорпус", sights: 0.07f, spread: -0.003f, mass: -0.0276f, bulk: 0.0552f, value: 163f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Ствол",true,
                    new ModuleOption("Штурмовой короткий", spread: 0.01f, sway: -0.04f, cooldown: -0.0255f, mass: -0.18f, bulk: -0.14f, steel: 4),
                    new ModuleOption("Средний утолщённый", spread: -0.01f, sway: 0.04f, mass: 0.28f, bulk: 0.19f, value: 30f, steel: 5, industrial: 1),
                    new ModuleOption("Штурмовой ультракороткий ствол", spread: 0.017f, mass: -0.2484f, bulk: -0.184f, value: 15f, range: -0.07f, steel: 3),
                    new ModuleOption("Тяжёлый средний ствол", spread: -0.012f, sway: 0.06f, mass: 0.3956f, bulk: 0.2208f, value: 74f, range: 0.09f, steel: 6, industrial: 1),
                    new ModuleOption("Охлаждаемый активный ствол", spread: -0.018f, mass: 0.1196f, bulk: 0.1012f, value: 180f, range: 0.12f, steel: 4, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Затвор",true,
                    new ModuleOption("Высокоскоростной", cooldown: -0.034f, mass: -0.08f, recoil: 0.075f, steel: 2, industrial: 1),
                    new ModuleOption("Демпфированный", cooldown: 0.034f, mass: 0.16f, value: 25f, recoil: -0.1f, steel: 6, industrial: 2),
                    new ModuleOption("Упрощённый скоростной затвор", cooldown: -0.06f, mass: -0.0644f, value: 18f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Усиленный затворный привод", cooldown: -0.04f, mass: 0.1196f, value: 85f, recoil: -0.075f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Электромагнитный цикл", cooldown: -0.075f, mass: 0.1656f, value: 197f, recoil: -0.035f, reload: -0.055f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Газоотвод",true,
                    new ModuleOption("Форсированный", cooldown: -0.0255f, mass: -0.07f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Адаптивный", cooldown: 0.02125f, mass: 0.11f, value: 38f, recoil: -0.08f, steel: 3, industrial: 1),
                    new ModuleOption("Газоотвод фиксированного давления", cooldown: -0.04f, mass: -0.0552f, value: 21f, recoil: 0.095f, steel: 2, industrial: 1),
                    new ModuleOption("Сервогазоотвод", cooldown: 0.025f, mass: 0.1288f, value: 96f, recoil: -0.11f, steel: 8, industrial: 1),
                    new ModuleOption("Плазморегулятор подачи", spread: -0.004f, cooldown: -0.02f, mass: 0.1564f, value: 214f, recoil: -0.065f, steel: 3, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Спуск",true,
                    new ModuleOption("Боевой", spread: 0.004f, mass: -0.02f, warmup: -0.04f, steel: 4),
                    new ModuleOption("Электронный", sights: 0.07f, spread: -0.008f, value: 36f, warmup: 0.015f, steel: 4, industrial: 2),
                    new ModuleOption("Штампованный спуск", spread: 0.012f, value: 24f, warmup: -0.055f, steel: 3),
                    new ModuleOption("Двухконтурный спуск", sights: 0.025f, spread: -0.009f, value: 107f, warmup: 0.015f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Прогнозирующий нейроспуск", sights: 0.12f, spread: -0.003f, value: 231f, warmup: -0.095f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Возвратная пружина",true,
                    new ModuleOption("Жёсткая", cooldown: -0.03825f, recoil: 0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Стабилизирующая", cooldown: 0.0425f, mass: 0.15f, value: 30f, recoil: -0.12f, steel: 5, industrial: 1),
                    new ModuleOption("Жёсткий возвратный узел", cooldown: -0.08f, mass: -0.0644f, value: 27f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Гидравлический буфер", cooldown: 0.025f, mass: 0.2208f, value: 118f, recoil: -0.15f, steel: 5, industrial: 1),
                    new ModuleOption("Активный импульсный демпфер", cooldown: -0.03f, mass: 0.1932f, value: 248f, recoil: -0.14f, steel: 2, industrial: 1, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Приклад",true,
                    new ModuleOption("Телескопический", sway: 0.1f, mass: -0.23f, bulk: -0.28f, steel: 3),
                    new ModuleOption("Гироскопический", sway: -0.09f, mass: 0.22f, bulk: 0.22f, value: 29f, recoil: -0.07f, steel: 6, industrial: 2),
                    new ModuleOption("Проволочный складной приклад", sway: 0.15f, mass: -0.23f, bulk: -0.322f, value: 30f, steel: 2),
                    new ModuleOption("Тяжёлый тактический приклад", sway: -0.13f, mass: 0.322f, bulk: 0.276f, value: 129f, recoil: -0.065f, steel: 6, industrial: 2, advanced: 1),
                    new ModuleOption("Миниатюрный гироприклад", sway: -0.115f, mass: 0.2116f, bulk: 0.0736f, value: 265f, recoil: -0.13f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Цевьё",true,
                    new ModuleOption("Открытая вентиляция", spread: 0.006f, cooldown: -0.017f, mass: -0.2f, steel: 4),
                    new ModuleOption("Тепловой кожух", spread: -0.008f, sway: -0.07f, mass: 0.24f, value: 40f, steel: 3, industrial: 1),
                    new ModuleOption("Короткое перфорированное цевьё", spread: 0.007f, mass: -0.2116f, bulk: -0.1104f, value: 33f, steel: 3, industrial: 1),
                    new ModuleOption("Теплоизоляционное цевьё", spread: -0.01f, sway: -0.06f, mass: 0.2484f, value: 57f, steel: 7, industrial: 1),
                    new ModuleOption("Микроканальное охлаждение", spread: -0.012f, sway: -0.045f, cooldown: -0.035f, mass: 0.184f, value: 282f, steel: 4, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Магазин",true,
                    new ModuleOption("25 патронов", mass: -0.07f, bulk: -0.07f, reload: -0.07f, steel: 2, industrial: 1),
                    new ModuleOption("40 патронов", mass: 0.17f, bulk: 0.18f, value: 30f, reload: 0.1f, steel: 4, industrial: 2),
                    new ModuleOption("Быстросменный магазин", mass: -0.0736f, bulk: -0.0828f, value: 36f, reload: -0.16f, steel: 1),
                    new ModuleOption("Упрочнённый магазин", mass: 0.2392f, bulk: 0.2208f, value: 68f, reload: 0.16f, steel: 8, industrial: 2, advanced: 1),
                    new ModuleOption("Диагностический смарт-магазин", cooldown: -0.012f, mass: 0.1012f, bulk: 0.0552f, value: 299f, reload: -0.1f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Прицел",false,
                    new ModuleOption("Голографический", sights: -0.05f, mass: -0.05f, steel: 3),
                    new ModuleOption("Нейрорефлексный", sights: 0.22f, mass: 0.13f, value: 66f, warmup: -0.075f, nightVision: 0.1f, steel: 5, industrial: 1, advanced: 1),
                    new ModuleOption("Открытый коллиматор", sights: -0.025f, mass: -0.0644f, value: 39f, warmup: -0.035f, steel: 2),
                    new ModuleOption("Штурмовой мультиприцел", sights: 0.28f, mass: 0.2576f, value: 79f, warmup: 0.055f, steel: 4, industrial: 1),
                    new ModuleOption("Нейрорефлексный прицел", sights: 0.2f, mass: 0.1472f, value: 159f, warmup: -0.12f, nightVision: 0.18f, steel: 3, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Рукоять",true,
                    new ModuleOption("Тактическая", sway: 0.03f, mass: -0.07f, steel: 4),
                    new ModuleOption("Датчиковая", sway: -0.05f, mass: 0.055f, value: 26f, recoil: -0.04f, steel: 6, industrial: 2),
                    new ModuleOption("Текстурная рукоять", sway: 0.05f, mass: -0.0828f, value: 11f, steel: 3),
                    new ModuleOption("Сервосцепление рукояти", sway: -0.11f, mass: 0.1012f, value: 90f, recoil: -0.03f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Биометрическая рукоять", sway: -0.12f, mass: 0.0644f, value: 176f, warmup: -0.045f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Переводчик огня",true,
                    new ModuleOption("Механический", cooldown: 0.0085f, reload: -0.03f, steel: 2, industrial: 1),
                    new ModuleOption("Программируемый", mass: 0.09f, value: 30f, reload: -0.12f, steel: 3, industrial: 1, advanced: 1),
                    new ModuleOption("Двусторонний переключатель", mass: 0.0184f, value: 14f, reload: -0.06f, steel: 1, industrial: 1),
                    new ModuleOption("Автоматический селектор", mass: 0.1564f, bulk: 0.0598f, value: 101f, reload: -0.17f, steel: 6, industrial: 1),
                    new ModuleOption("Динамический предиктор очереди", cooldown: -0.04f, mass: 0.0782f, value: 193f, reload: -0.11f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Дульное устройство",false,
                    new ModuleOption("Пламегаситель", mass: -0.05f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Активный компенсатор", spread: -0.006f, mass: 0.16f, bulk: 0.06f, value: 34f, recoil: -0.12f, steel: 4, industrial: 2),
                    new ModuleOption("Короткий пламегаситель", mass: 0.046f, bulk: 0.0322f, value: 17f, recoil: -0.035f, steel: 2),
                    new ModuleOption("Многокамерный ДТК", mass: 0.1656f, bulk: 0.092f, value: 112f, recoil: -0.19f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Активный векторный компенсатор", spread: -0.005f, mass: 0.1288f, value: 210f, recoil: -0.12f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Нижняя аксессуарная планка",false,
                    new ModuleOption("Базовая нижняя планка", mass: 0.04f, bulk: 0.04f, steel: 3),
                    new ModuleOption("Облегчённая рельса", sway: 0.02f, mass: -0.08f, steel: 2, industrial: 1),
                    new ModuleOption("Усиленная рельса", sway: -0.04f, mass: 0.2f, recoil: -0.02f, steel: 4, industrial: 2),
                    new ModuleOption("Многопозиционный кронштейн", sights: 0.04f, mass: 0.16f, warmup: -0.015f, steel: 3, industrial: 2, advanced: 1),
                    new ModuleOption("Умная интерфейсная рельса", sights: 0.07f, mass: 0.1f, value: 140f, nightVision: 0.03f, steel: 2, industrial: 1, advanced: 3, gold: 5)
                ),
            },
            new ModuleSlot[] {
                new ModuleSlot("Затворная рама",true,
                    new ModuleOption("Одиночный цикл", sway: 0.045f, cooldown: -0.03f, mass: -0.027f, steel: 2, industrial: 1),
                    new ModuleOption("Трёхвыстрельная отсечка", sights: 0.09f, spread: -0.004f, cooldown: 0.03f, mass: 0.0495f, recoil: -0.06f, steel: 3, industrial: 1),
                    new ModuleOption("Упрощённый ударниковый цикл", cooldown: -0.07f, mass: -0.0594f, value: 9f, recoil: 0.15f, steel: 1, industrial: 1),
                    new ModuleOption("Электронный цикл затвора", cooldown: -0.025f, mass: 0.1026f, value: 52f, recoil: -0.11f, warmup: 0.025f, steel: 4, industrial: 1),
                    new ModuleOption("Программируемый интеллектуальный затвор", sights: 0.08f, cooldown: -0.065f, mass: 0.108f, value: 146f, recoil: -0.045f, warmup: -0.025f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Рамка",true,
                    new ModuleOption("Полимерная", sway: 0.045f, mass: -0.0585f, bulk: -0.05f, steel: 3),
                    new ModuleOption("Армированная", sights: 0.04f, spread: -0.003f, mass: 0.045f, bulk: 0.025f, value: 36f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Штампованная облегчённая рамка", spread: 0.006f, mass: -0.1188f, bulk: -0.0648f, value: 12f, steel: 2),
                    new ModuleOption("Титановая рамка", spread: -0.006f, mass: 0.0864f, bulk: 0.0486f, value: 63f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Морфирующая экзорамка", sights: 0.07f, spread: -0.003f, mass: -0.0162f, bulk: 0.0324f, value: 163f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Ствол",true,
                    new ModuleOption("Компактный", spread: 0.01f, sway: -0.04f, cooldown: -0.03f, mass: -0.081f, bulk: -0.07f, steel: 4),
                    new ModuleOption("Удлинённый", spread: -0.01f, sway: 0.04f, mass: 0.126f, bulk: 0.095f, value: 30f, steel: 5, industrial: 1),
                    new ModuleOption("Ультракороткий ствол", spread: 0.017f, mass: -0.1458f, bulk: -0.108f, value: 15f, range: -0.07f, steel: 3),
                    new ModuleOption("Матчевый ствол", spread: -0.012f, sway: 0.06f, mass: 0.2322f, bulk: 0.1296f, value: 74f, range: 0.09f, steel: 6, industrial: 1),
                    new ModuleOption("Стабилизированный наноствол", spread: -0.018f, mass: 0.0702f, bulk: 0.0594f, value: 180f, range: 0.12f, steel: 4, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Затвор",true,
                    new ModuleOption("Облегчённый", cooldown: -0.04f, mass: -0.036f, recoil: 0.075f, steel: 2, industrial: 1),
                    new ModuleOption("Утяжелённый", cooldown: 0.04f, mass: 0.072f, value: 25f, recoil: -0.1f, steel: 6, industrial: 2),
                    new ModuleOption("Тонкий полусвободный затвор", cooldown: -0.06f, mass: -0.0378f, value: 18f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Упрочнённый затвор", cooldown: -0.04f, mass: 0.0702f, value: 85f, recoil: -0.075f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Электромагнитный привод затвора", cooldown: -0.075f, mass: 0.0972f, value: 197f, recoil: -0.035f, reload: -0.055f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Экстрактор",true,
                    new ModuleOption("Пружинный", cooldown: -0.03f, mass: -0.0315f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Электромагнитный", cooldown: 0.025f, mass: 0.0495f, value: 38f, recoil: -0.08f, steel: 3, industrial: 1),
                    new ModuleOption("Простой экстрактор", cooldown: -0.04f, mass: -0.0324f, value: 21f, recoil: 0.095f, steel: 2, industrial: 1),
                    new ModuleOption("Двойной экстрактор", cooldown: 0.025f, mass: 0.0756f, value: 96f, recoil: -0.11f, steel: 8, industrial: 1),
                    new ModuleOption("Магнитный экстрактор", spread: -0.004f, cooldown: -0.02f, mass: 0.0918f, value: 214f, recoil: -0.065f, steel: 3, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Спуск",true,
                    new ModuleOption("Двойного действия", spread: 0.004f, mass: -0.009f, warmup: -0.04f, steel: 4),
                    new ModuleOption("Сенсорный", sights: 0.07f, spread: -0.008f, value: 36f, warmup: 0.015f, steel: 4, industrial: 2),
                    new ModuleOption("Стандартный спуск", spread: 0.012f, value: 24f, warmup: -0.055f, steel: 3),
                    new ModuleOption("Матчевый двойной спуск", sights: 0.025f, spread: -0.009f, value: 107f, warmup: 0.015f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Биометрический спуск", sights: 0.12f, spread: -0.003f, value: 231f, warmup: -0.095f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Возвратная пружина",true,
                    new ModuleOption("Компактная", cooldown: -0.045f, recoil: 0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Мягкая", cooldown: 0.05f, mass: 0.0675f, value: 30f, recoil: -0.12f, steel: 5, industrial: 1),
                    new ModuleOption("Жёсткая возвратная пружина", cooldown: -0.08f, mass: -0.0378f, value: 27f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Масляный демпфер", cooldown: 0.025f, mass: 0.1296f, value: 118f, recoil: -0.15f, steel: 5, industrial: 1),
                    new ModuleOption("Магнитный амортизатор", cooldown: -0.03f, mass: 0.1134f, value: 248f, recoil: -0.14f, steel: 2, industrial: 1, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Задняя панель рукояти",true,
                    new ModuleOption("Обтекаемая", sway: 0.1f, mass: -0.1035f, bulk: -0.14f, steel: 3),
                    new ModuleOption("Стабилизирующая", sway: -0.09f, mass: 0.099f, bulk: 0.11f, value: 29f, recoil: -0.07f, steel: 6, industrial: 2),
                    new ModuleOption("Тонкая тыльная накладка", sway: 0.15f, mass: -0.135f, bulk: -0.189f, value: 30f, steel: 2),
                    new ModuleOption("Контурный упор ладони", sway: -0.13f, mass: 0.189f, bulk: 0.162f, value: 129f, recoil: -0.065f, steel: 6, industrial: 2, advanced: 1),
                    new ModuleOption("Активный противооткатный упор", sway: -0.115f, mass: 0.1242f, bulk: 0.0432f, value: 265f, recoil: -0.13f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Кожух затвора",true,
                    new ModuleOption("Открытый", spread: 0.006f, cooldown: -0.02f, mass: -0.09f, steel: 4),
                    new ModuleOption("Термокожух", spread: -0.008f, sway: -0.07f, mass: 0.108f, value: 40f, steel: 3, industrial: 1),
                    new ModuleOption("Открытый кожух затвора", spread: 0.007f, mass: -0.1242f, bulk: -0.0648f, value: 33f, steel: 3, industrial: 1),
                    new ModuleOption("Карбоновый термокожух", spread: -0.01f, sway: -0.06f, mass: 0.1458f, value: 57f, steel: 7, industrial: 1),
                    new ModuleOption("Криоэкран затвора", spread: -0.012f, sway: -0.045f, cooldown: -0.035f, mass: 0.108f, value: 282f, steel: 4, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Магазин",true,
                    new ModuleOption("12 патронов", mass: -0.0315f, bulk: -0.035f, reload: -0.07f, steel: 2, industrial: 1),
                    new ModuleOption("20 патронов", mass: 0.0765f, bulk: 0.09f, value: 30f, reload: 0.1f, steel: 4, industrial: 2),
                    new ModuleOption("Облегчённый магазин", mass: -0.0432f, bulk: -0.0486f, value: 36f, reload: -0.16f, steel: 1),
                    new ModuleOption("Упрочнённый магазин", mass: 0.1404f, bulk: 0.1296f, value: 68f, reload: 0.16f, steel: 8, industrial: 2, advanced: 1),
                    new ModuleOption("Смарт-магазин пистолета", cooldown: -0.012f, mass: 0.0594f, bulk: 0.0324f, value: 299f, reload: -0.1f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Прицел",false,
                    new ModuleOption("Тритиевый", sights: -0.05f, mass: -0.0225f, steel: 3),
                    new ModuleOption("Компактный коллиматор", sights: 0.22f, mass: 0.0585f, value: 66f, warmup: -0.075f, nightVision: 0.1f, steel: 5, industrial: 1, advanced: 1),
                    new ModuleOption("Открытые механические прицельные", sights: -0.025f, mass: -0.0378f, value: 39f, warmup: -0.035f, steel: 2),
                    new ModuleOption("Компактная гибридная оптика", sights: 0.28f, mass: 0.1512f, value: 79f, warmup: 0.055f, steel: 4, industrial: 1),
                    new ModuleOption("Нейросинхронизированная оптика", sights: 0.2f, mass: 0.0864f, value: 159f, warmup: -0.12f, nightVision: 0.18f, steel: 3, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Накладки рукояти",true,
                    new ModuleOption("Шероховатые", sway: 0.03f, mass: -0.0315f, steel: 4),
                    new ModuleOption("Биометрические", sway: -0.05f, mass: 0.02475f, value: 26f, recoil: -0.04f, steel: 6, industrial: 2),
                    new ModuleOption("Рифлёные накладки", sway: 0.05f, mass: -0.0486f, value: 11f, steel: 3),
                    new ModuleOption("Тактическая текстура", sway: -0.11f, mass: 0.0594f, value: 90f, recoil: -0.03f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Сенсорная подладонная рукоять", sway: -0.12f, mass: 0.0378f, value: 176f, warmup: -0.045f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Затворная задержка",true,
                    new ModuleOption("Ручная", cooldown: 0.01f, reload: -0.03f, steel: 2, industrial: 1),
                    new ModuleOption("Автоматическая", mass: 0.0405f, value: 30f, reload: -0.12f, steel: 3, industrial: 1, advanced: 1),
                    new ModuleOption("Механическая затворная задержка", mass: 0.0108f, value: 14f, reload: -0.06f, steel: 1, industrial: 1),
                    new ModuleOption("Самосбрасываемая задержка", mass: 0.0918f, bulk: 0.0351f, value: 101f, reload: -0.17f, steel: 6, industrial: 1),
                    new ModuleOption("Электронная задержка", cooldown: -0.04f, mass: 0.0459f, value: 193f, reload: -0.11f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Насадка на ствол",false,
                    new ModuleOption("Защитная", mass: -0.0225f, recoil: 0.055f, steel: 3),
                    new ModuleOption("Компенсирующая", spread: -0.006f, mass: 0.072f, bulk: 0.03f, value: 34f, recoil: -0.12f, steel: 4, industrial: 2),
                    new ModuleOption("Простой защитный колпачок", mass: 0.027f, bulk: 0.0189f, value: 17f, recoil: -0.035f, steel: 2),
                    new ModuleOption("Двухкамерный тормоз", mass: 0.0972f, bulk: 0.054f, value: 112f, recoil: -0.19f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Активный компенсатор пистолета", spread: -0.005f, mass: 0.0756f, value: 210f, recoil: -0.12f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Нижняя аксессуарная планка",false,
                    new ModuleOption("Базовая нижняя планка", mass: 0.04f, bulk: 0.04f, steel: 3),
                    new ModuleOption("Облегчённая рельса", sway: 0.02f, mass: -0.08f, steel: 2, industrial: 1),
                    new ModuleOption("Усиленная рельса", sway: -0.04f, mass: 0.2f, recoil: -0.02f, steel: 4, industrial: 2),
                    new ModuleOption("Многопозиционный кронштейн", sights: 0.04f, mass: 0.16f, warmup: -0.015f, steel: 3, industrial: 2, advanced: 1),
                    new ModuleOption("Умная интерфейсная рельса", sights: 0.07f, mass: 0.1f, value: 140f, nightVision: 0.03f, steel: 2, industrial: 1, advanced: 3, gold: 5)
                ),
            },
            new ModuleSlot[] {
                new ModuleSlot("Блок управления",true,
                    new ModuleOption("Одиночный подрывной цикл", sway: 0.045f, cooldown: -0.03f, mass: -0.06f, steel: 2, industrial: 1),
                    new ModuleOption("Двойной последовательный залп", sights: 0.09f, spread: -0.0048f, cooldown: 0.03f, mass: 0.11f, recoil: -0.0696f, steel: 3, industrial: 1),
                    new ModuleOption("Упрощённый блок подрыва", cooldown: -0.07f, mass: -0.1265f, value: 9f, recoil: 0.15f, steel: 1, industrial: 1),
                    new ModuleOption("Управляемый последовательный цикл", cooldown: -0.025f, mass: 0.2185f, value: 52f, recoil: -0.11f, warmup: 0.025f, steel: 4, industrial: 1),
                    new ModuleOption("Интеллектуальный контроллер залпа", sights: 0.08f, cooldown: -0.065f, mass: 0.23f, value: 146f, recoil: -0.045f, warmup: -0.025f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Ствольная коробка",true,
                    new ModuleOption("Усиленная стальная", sway: 0.045f, mass: -0.13f, bulk: -0.1f, steel: 3),
                    new ModuleOption("Композитная", sights: 0.04f, spread: -0.0036f, mass: 0.1f, bulk: 0.05f, value: 36f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Сварной стальной ресивер", spread: 0.006f, mass: -0.253f, bulk: -0.138f, value: 12f, steel: 2),
                    new ModuleOption("Керамический герморесивер", spread: -0.006f, mass: 0.184f, bulk: 0.1035f, value: 63f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Наноплетёная ствольная коробка", sights: 0.07f, spread: -0.003f, mass: -0.0345f, bulk: 0.069f, value: 163f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Ствол",true,
                    new ModuleOption("Короткий гранатомётный", spread: 0.012f, sway: -0.04f, cooldown: -0.03f, mass: -0.18f, bulk: -0.14f, steel: 4),
                    new ModuleOption("Длинный стабилизированный", spread: -0.012f, sway: 0.04f, mass: 0.28f, bulk: 0.19f, value: 30f, steel: 5, industrial: 1),
                    new ModuleOption("Укороченный гранатный ствол", spread: 0.017f, mass: -0.3105f, bulk: -0.23f, value: 15f, range: -0.07f, steel: 3),
                    new ModuleOption("Тяжёлый нарезной ствол", spread: -0.012f, sway: 0.06f, mass: 0.4945f, bulk: 0.276f, value: 74f, range: 0.09f, steel: 6, industrial: 1),
                    new ModuleOption("Активный гироствол", spread: -0.018f, mass: 0.1495f, bulk: 0.1265f, value: 180f, range: 0.12f, steel: 4, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Затвор",true,
                    new ModuleOption("Механическая казённая часть", cooldown: -0.04f, mass: -0.08f, recoil: 0.087f, steel: 2, industrial: 1),
                    new ModuleOption("Герметизированный блок", cooldown: 0.04f, mass: 0.16f, value: 25f, recoil: -0.116f, steel: 6, industrial: 2),
                    new ModuleOption("Простая казённая крышка", cooldown: -0.06f, mass: -0.0805f, value: 18f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Усиленный гермозатвор", cooldown: -0.04f, mass: 0.1495f, value: 85f, recoil: -0.075f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Электропривод затвора", cooldown: -0.075f, mass: 0.207f, value: 197f, recoil: -0.035f, reload: -0.055f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Механизм подачи",true,
                    new ModuleOption("Храповик", cooldown: -0.03f, mass: -0.07f, recoil: 0.0638f, steel: 3),
                    new ModuleOption("Сервопривод", cooldown: 0.025f, mass: 0.11f, value: 38f, recoil: -0.0928f, steel: 3, industrial: 1),
                    new ModuleOption("Механическая подача", cooldown: -0.04f, mass: -0.069f, value: 21f, recoil: 0.095f, steel: 2, industrial: 1),
                    new ModuleOption("Прецизионный барабанный привод", cooldown: 0.025f, mass: 0.161f, value: 96f, recoil: -0.11f, steel: 8, industrial: 1),
                    new ModuleOption("Предиктивный сервопривод барабана", spread: -0.004f, cooldown: -0.02f, mass: 0.1955f, value: 214f, recoil: -0.065f, steel: 3, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Спуск",true,
                    new ModuleOption("Механический", spread: 0.0048f, mass: -0.02f, warmup: -0.04f, steel: 4),
                    new ModuleOption("Дистанционный электро-спуск", sights: 0.07f, spread: -0.0096f, value: 36f, warmup: 0.015f, steel: 4, industrial: 2),
                    new ModuleOption("Рычажный спуск", spread: 0.012f, value: 24f, warmup: -0.055f, steel: 3),
                    new ModuleOption("Электроспуск с блокировкой", sights: 0.025f, spread: -0.009f, value: 107f, warmup: 0.015f, steel: 4, industrial: 2, advanced: 1),
                    new ModuleOption("Нейроспуск с датчиком цели", sights: 0.12f, spread: -0.003f, value: 231f, warmup: -0.095f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Возврат/амортизатор",true,
                    new ModuleOption("Пружинный", cooldown: -0.045f, recoil: 0.0696f, steel: 2, industrial: 1),
                    new ModuleOption("Гидравлический", cooldown: 0.05f, mass: 0.15f, value: 30f, recoil: -0.1392f, steel: 5, industrial: 1),
                    new ModuleOption("Простая возвратная пружина", cooldown: -0.08f, mass: -0.0805f, value: 27f, recoil: 0.14f, steel: 1),
                    new ModuleOption("Тяжёлый гидродемпфер", cooldown: 0.025f, mass: 0.276f, value: 118f, recoil: -0.15f, steel: 5, industrial: 1),
                    new ModuleOption("Магнитный противооткатный блок", cooldown: -0.03f, mass: 0.2415f, value: 248f, recoil: -0.14f, steel: 2, industrial: 1, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Приклад",true,
                    new ModuleOption("Откидной", sway: 0.1f, mass: -0.23f, bulk: -0.28f, steel: 3),
                    new ModuleOption("Противооткатный", sway: -0.09f, mass: 0.22f, bulk: 0.22f, value: 29f, recoil: -0.0812f, steel: 6, industrial: 2),
                    new ModuleOption("Лёгкий рамочный приклад", sway: 0.15f, mass: -0.2875f, bulk: -0.4025f, value: 30f, steel: 2),
                    new ModuleOption("Жёсткий противооткатный приклад", sway: -0.13f, mass: 0.4025f, bulk: 0.345f, value: 129f, recoil: -0.065f, steel: 6, industrial: 2, advanced: 1),
                    new ModuleOption("Гиростабилизирующий приклад", sway: -0.115f, mass: 0.2645f, bulk: 0.092f, value: 265f, recoil: -0.13f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Цевьё",true,
                    new ModuleOption("Сетчатое", spread: 0.0072f, cooldown: -0.02f, mass: -0.2f, steel: 4),
                    new ModuleOption("Изолированное", spread: -0.0096f, sway: -0.07f, mass: 0.24f, value: 40f, steel: 3, industrial: 1),
                    new ModuleOption("Перфорированный экран", spread: 0.007f, mass: -0.2645f, bulk: -0.138f, value: 33f, steel: 3, industrial: 1),
                    new ModuleOption("Термокерамический кожух", spread: -0.01f, sway: -0.06f, mass: 0.3105f, value: 57f, steel: 7, industrial: 1),
                    new ModuleOption("Криоактивное цевьё", spread: -0.012f, sway: -0.045f, cooldown: -0.035f, mass: 0.23f, value: 282f, steel: 4, industrial: 1, advanced: 2, gold: 9)
                ),
                new ModuleSlot("Барабан",true,
                    new ModuleOption("3 гранаты", mass: -0.07f, bulk: -0.07f, reload: -0.07f, steel: 2, industrial: 1),
                    new ModuleOption("6 гранат", mass: 0.17f, bulk: 0.18f, value: 30f, reload: 0.1f, steel: 4, industrial: 2),
                    new ModuleOption("Лёгкий барабан", mass: -0.092f, bulk: -0.1035f, value: 36f, reload: -0.16f, steel: 1),
                    new ModuleOption("Усиленный барабан", mass: 0.299f, bulk: 0.276f, value: 68f, reload: 0.16f, steel: 8, industrial: 2, advanced: 1),
                    new ModuleOption("Барабан с диагностикой камор", cooldown: -0.012f, mass: 0.1265f, bulk: 0.069f, value: 299f, reload: -0.1f, steel: 2, industrial: 2, advanced: 3, gold: 4)
                ),
                new ModuleSlot("Прицельный комплекс",false,
                    new ModuleOption("Лестничный", sights: -0.05f, mass: -0.05f, steel: 3),
                    new ModuleOption("Дальномерный", sights: 0.22f, mass: 0.13f, value: 66f, warmup: -0.075f, nightVision: 0.1f, steel: 5, industrial: 1, advanced: 1),
                    new ModuleOption("Лестничный резервный прицел", sights: -0.025f, mass: -0.0805f, value: 39f, warmup: -0.035f, steel: 2),
                    new ModuleOption("Дальномерная оптика", sights: 0.28f, mass: 0.322f, value: 79f, warmup: 0.055f, steel: 4, industrial: 1),
                    new ModuleOption("Интеллектуальный баллистический вычислитель", sights: 0.2f, mass: 0.184f, value: 159f, warmup: -0.12f, nightVision: 0.18f, steel: 3, industrial: 1, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Рукоять",true,
                    new ModuleOption("Резиновая", sway: 0.03f, mass: -0.07f, steel: 4),
                    new ModuleOption("Экзоприводная", sway: -0.05f, mass: 0.055f, value: 26f, recoil: -0.0464f, steel: 6, industrial: 2),
                    new ModuleOption("Резиновая полевая рукоять", sway: 0.05f, mass: -0.1035f, value: 11f, steel: 3),
                    new ModuleOption("Противооткатная рукоять", sway: -0.11f, mass: 0.1265f, value: 90f, recoil: -0.03f, steel: 5, industrial: 2, advanced: 1),
                    new ModuleOption("Нейрогироскопическая рукоять", sway: -0.12f, mass: 0.0805f, value: 176f, warmup: -0.045f, steel: 4, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Замок барабана",true,
                    new ModuleOption("Ручной", cooldown: 0.01f, reload: -0.03f, steel: 2, industrial: 1),
                    new ModuleOption("Автосброс", mass: 0.09f, value: 30f, reload: -0.12f, steel: 3, industrial: 1, advanced: 1),
                    new ModuleOption("Ручной фиксатор барабана", mass: 0.023f, value: 14f, reload: -0.06f, steel: 1, industrial: 1),
                    new ModuleOption("Сервозамок", mass: 0.1955f, bulk: 0.07475f, value: 101f, reload: -0.17f, steel: 6, industrial: 1),
                    new ModuleOption("Автоматический синхрозамок", cooldown: -0.04f, mass: 0.09775f, value: 193f, reload: -0.11f, steel: 2, industrial: 1, advanced: 3, gold: 9)
                ),
                new ModuleSlot("Надульный узел",false,
                    new ModuleOption("Раструб", mass: -0.05f, recoil: 0.0638f, steel: 3),
                    new ModuleOption("Газовый диффузор", spread: -0.0072f, mass: 0.16f, bulk: 0.06f, value: 34f, recoil: -0.1392f, steel: 4, industrial: 2),
                    new ModuleOption("Простой защитный раструб", mass: 0.0575f, bulk: 0.04025f, value: 17f, recoil: -0.035f, steel: 2),
                    new ModuleOption("Диффузор отдачи", mass: 0.207f, bulk: 0.115f, value: 112f, recoil: -0.19f, steel: 7, industrial: 2, advanced: 1),
                    new ModuleOption("Активный газовый модулятор", spread: -0.005f, mass: 0.161f, value: 210f, recoil: -0.12f, steel: 3, industrial: 2, advanced: 2, gold: 4)
                ),
                new ModuleSlot("Нижняя аксессуарная планка",false,
                    new ModuleOption("Базовая нижняя планка", mass: 0.04f, bulk: 0.04f, steel: 3),
                    new ModuleOption("Облегчённая рельса", sway: 0.02f, mass: -0.08f, steel: 2, industrial: 1),
                    new ModuleOption("Усиленная рельса", sway: -0.04f, mass: 0.2f, recoil: -0.02f, steel: 4, industrial: 2),
                    new ModuleOption("Многопозиционный кронштейн", sights: 0.04f, mass: 0.16f, warmup: -0.015f, steel: 3, industrial: 2, advanced: 1),
                    new ModuleOption("Умная интерфейсная рельса", sights: 0.07f, mass: 0.1f, value: 140f, nightVision: 0.03f, steel: 2, industrial: 1, advanced: 3, gold: 5)
                ),
            },
        };
        public static WeaponFamily Family(int id) => Families[id>=0 && id<Families.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(int id) => Slots[id>=0 && id<Slots.Length ? id : 0];
        public static ModuleSlot[] RequiredFor(WeaponBlueprint b) => RequiredFor(b?.FamilyId ?? 0);
        public static bool IsOurWeapon(string name) => name!=null &&
           (name.StartsWith("TT_Rifle_R", StringComparison.Ordinal) || name.StartsWith("TT_Auto_R", StringComparison.Ordinal) ||
            name.StartsWith("TT_Pistol_R", StringComparison.Ordinal) || name.StartsWith("TT_Launcher_R", StringComparison.Ordinal));
        public static int FamilyFromDef(string name)
        {
            if (name!=null) for(int i=0;i<Families.Length;i++)
                if(name.StartsWith("TT_"+Families[i].Key+"_R", StringComparison.Ordinal))return i;
            return 0;
        }
        // Three identical optional slots; different modules may affect the same assembly.
        public static readonly SpecialModule[] Specials = {
            new SpecialModule("Прицел", "Лазерный целеуказатель", "Дешёвая помощь при наведении", new ModuleOption("Лазерный целеуказатель", sights: 0.13f, sway: -0.035f, mass: 0.12f, value: 45f, warmup: -0.075f, steel: 3, industrial: 1)),
            new SpecialModule("Прицел", "Спектральный усилитель", "Оптический усилитель в условиях недостаточного света", new ModuleOption("Спектральный усилитель", sights: 0.09f, mass: 0.19f, value: 105f, nightVision: 0.24f, steel: 2, industrial: 1, advanced: 1)),
            new SpecialModule("Прицел", "Нейро-связь оптики", "Быстрый прицельный цикл, дорогой в ремонте", new ModuleOption("Нейро-связь оптики", sights: 0.19f, sway: -0.035f, mass: 0.25f, value: 170f, warmup: -0.13f, steel: 2, industrial: 1, advanced: 2, gold: 5)),
            new SpecialModule("Коробка", "Электронный спуск", "Малая задержка между сериями, уязвим к сбоям", new ModuleOption("Электронный спуск", cooldown: -0.085f, mass: 0.1f, value: 105f, warmup: -0.015f, steel: 1, industrial: 2)),
            new SpecialModule("Коробка", "Затворный стабилизатор", "Снижение отдачи ценой веса", new ModuleOption("Затворный стабилизатор", sway: -0.035f, mass: 0.18f, value: 125f, recoil: -0.15f, steel: 8, industrial: 1)),
            new SpecialModule("Коробка", "Система быстрого досылания", "Ускорение подготовки патронов", new ModuleOption("Система быстрого досылания", mass: 0.18f, value: 95f, reload: -0.16f, steel: 5, industrial: 2)),
            new SpecialModule("Цевьё", "Сервостабилизатор", "Снижение раскачивания в позиции", new ModuleOption("Сервостабилизатор", sway: -0.17f, mass: 0.3f, bulk: 0.12f, value: 135f, recoil: -0.06f, steel: 6, industrial: 1, advanced: 1)),
            new SpecialModule("Ствол", "Термокомпенсатор", "Компенсирует деформацию нагретого ствола", new ModuleOption("Термокомпенсатор", spread: -0.014f, mass: 0.28f, value: 125f, steel: 7, industrial: 2)),
            new SpecialModule("Магазин", "Интеллектуальная подача", "Ускоряет работу магазина, не меняя баллистику", new ModuleOption("Интеллектуальная подача", cooldown: -0.025f, mass: 0.12f, value: 110f, reload: -0.13f, steel: 2, industrial: 2, advanced: 1)),
            new SpecialModule("Прицел", "Призменный дальномер", "Уверенное считывание дальности на дистанции", new ModuleOption("Призменный дальномер", sights: 0.16f, mass: 0.24f, value: 126f, warmup: 0.04f, range: 0.05f, steel: 4, industrial: 2, advanced: 1)),
            new SpecialModule("Прицел", "Контурная голограмма", "Быстрое ближнее наведение с недостатками вдали", new ModuleOption("Контурная голограмма", sights: 0.075f, spread: 0.004f, sway: -0.1f, mass: 0.19f, value: 59f, warmup: -0.07f, steel: 2, industrial: 2)),
            new SpecialModule("Коробка", "Система гашения импульса", "Мощный тяжелый демпфер для устойчивых серий", new ModuleOption("Система гашения импульса", cooldown: 0.055f, mass: 0.42f, bulk: 0.18f, value: 105f, recoil: -0.25f, steel: 11, industrial: 1)),
            new SpecialModule("Ствол", "Криоканальный охладитель", "Прогнозируемое смещение точек попаданий при долгом огне", new ModuleOption("Криоканальный охладитель", spread: -0.017f, sway: -0.035f, mass: 0.27f, bulk: 0.14f, value: 178f, steel: 4, industrial: 1, advanced: 2)),
            new SpecialModule("Коробка", "Электромагнитный затвор", "Стабильное досылание, дорогое энергоснабжение", new ModuleOption("Электромагнитный затвор", cooldown: -0.09f, mass: 0.22f, value: 224f, recoil: -0.045f, reload: -0.06f, steel: 5, industrial: 1, advanced: 3, gold: 2)),
            new SpecialModule("Прицел", "Псионический вычислитель", "Экспериментальный оптический синхронизатор; не меняет пули CE", new ModuleOption("Псионический вычислитель", sights: 0.24f, sway: -0.085f, mass: 0.3f, value: 405f, warmup: -0.115f, nightVision: 0.22f, steel: 3, industrial: 2, advanced: 3, gold: 12)),
        };
        public static string WeaponDefName(WeaponBlueprint b) =>
            $"TT_{Family(b.FamilyId).Key}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}" + (b.CaliberId==0 ? "" : "_C"+b.CaliberId);
        // One production RecipeDef per underlying CE structural variant (32 total); material
        // requirements are exact per blueprint and escrowed when the user queues the bill.
        public static string RecipeName(WeaponBlueprint b)
        {
            string prefix=b.FamilyId==0 ? "TT_Craft" : "TT_Craft_"+Family(b.FamilyId).Key;
            return $"{prefix}_R{b.CoreIndex(0)}_B{b.CoreIndex(2)}_M{b.CoreIndex(9)}" + (b.CaliberId==0 ? "" : "_C"+b.CaliberId);
        }
    }
}
