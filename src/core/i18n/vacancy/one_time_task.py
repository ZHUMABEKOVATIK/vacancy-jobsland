from src.models.vacancy import OneTimeTask
from src.core.i18n.vacancy.vacancy_types import TgPost

LABELS = {
    "eng": {
        'title': "Application",
        "hashtag": "#ProjectOrder #OneTimeTask",
        "who_needed": "Specialist",
        "task_description": "Task",
        "deadline": "Deadline",
        "salary": "Payment",
        "contact": "Contact",
        "address": "Location",
        "additional_info": "Additional info",
    },
    "rus": {
        'title': "Заявка",
        "hashtag": "#ПроектЗаказ #РазоваяРабота",
        "who_needed": "Специалист",
        "task_description": "Задача",
        "deadline": "Срок",
        "salary": "Оплата",
        "contact": "Контакты",
        "address": "Локация",
        "additional_info": "Дополнительно",
    },
    "kaa": {
        'title': "Soraw",
        "hashtag": "#ПроектЗаказ #БирМәртелик",
        "who_needed": "Qániyge",
        "task_description": "Tapsırma",
        "deadline": "Múddet",
        "salary": "Is haqı",
        "contact": "Baylanıs",
        "address": "Mánzil",
        "additional_info": "Qosımsha",
    },
    "uzb": {
        'title': "Ariza",
        "hashtag": "#ПроектЗаказ #BirMartalikIsh",
        "who_needed": "Mutaxassis",
        "task_description": "Vazifa",
        "deadline": "Muddat",
        "salary": "Ish haqi",
        "contact": "Aloqa",
        "address": "Manzil",
        "additional_info": "Qo‘shimcha",
    },
    "kaz": {
        'title': "Өтініш",
        "hashtag": "#ПроектЗаказ #БірРеттікЖұмыс",
        "who_needed": "Маман",
        "task_description": "Тапсырма",
        "deadline": "Мерзім",
        "salary": "Төлемақы",
        "contact": "Байланыс",
        "address": "Мекенжай",
        "additional_info": "Қосымша",
    },
    "kgz": {
        'title': "Өтүнүч",
        "hashtag": "#ПроектЗаказ #БирЖолкуИш",
        "who_needed": "Адис",
        "task_description": "Тапшырма",
        "deadline": "Мөөнөт",
        "salary": "Төлөм",
        "contact": "Байланыш",
        "address": "Жайгашкан жери",
        "additional_info": "Кошумча",
    },
    "tjk": {
        'title': "Дархост",
        "hashtag": "#ПроектЗаказ #КорЯкМартаба",
        "who_needed": "Мутахассис",
        "task_description": "Вазифа",
        "deadline": "Мӯҳлат",
        "salary": "Музд",
        "contact": "Тамос",
        "address": "Ҷойгиршавӣ",
        "additional_info": "Иловагӣ",
    },
    "aze": {
        'title': "Müraciət",
        "hashtag": "#ПроектЗаказ #BirDəfəlikİş",
        "who_needed": "Mütəxəssis",
        "task_description": "Tapşırıq",
        "deadline": "Müddət",
        "salary": "Ödəniş",
        "contact": "Əlaqə",
        "address": "Məkan",
        "additional_info": "Əlavə",
    },
    "tkm": {
        'title': "Arza",
        "hashtag": "#ПроектЗаказ #BirSaparlyIş",
        "who_needed": "Hünärmen",
        "task_description": "Wezipe",
        "deadline": "Möhlet",
        "salary": "Töleg",
        "contact": "Aragatnaşyk",
        "address": "Ýerleşýän ýeri",
        "additional_info": "Goşmaça",
    },
}

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: OneTimeTask) -> TgPost:
    d = LABELS.get(lang_code, LABELS["eng"])
    lines = [
        f"{d['hashtag']}\n",
        f"👨‍💼 <b>{d['who_needed']}</b>: {esc(post.who_needed)}",
        f"🏛 <b>{d['task_description']}</b>: {esc(post.task_description)}",
        f"💰 <b>{d['salary']}</b>: {esc(post.salary)}",
    ]
    if post.deadline:
        lines.append(f"⚙️ <b>{d['deadline']}</b>: {esc(post.deadline)}")
    lines += [
        f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}",
    ]
    if post.address:
        lines.append(f"⚙️ <b>{d['address']}</b>: {esc(post.address)}")
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")
    result = "\n".join(lines)
    return TgPost(text=result)

async def get_vacancy_group_format(post: OneTimeTask, lang_code: str = "kaa") -> str:
    d = LABELS.get(lang_code, LABELS["eng"])
    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"
    group_version = await get_vacancy_channel_format(lang_code=lang_code, post=post)
    return header + loc + group_version.text