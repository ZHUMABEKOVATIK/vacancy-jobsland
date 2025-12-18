# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm
from src.models.vacancy import Internship
from src.core.i18n.vacancy.vacancy_types import TgPost

LABELS = {
    "eng": {
        'title': "Application",
        "hashtag": "#Internship #Стажировка",
        "position_title": "Position",
        "organization_name": "Company",
        "requirements": "Requirements",
        "duties": "Responsibilities",
        "conditions": "Conditions",
        "address": "Location",
        "salary": "Payment",
        "contact": "Contact",
        "additional_info": "Additional Info",
    },
    "rus": {
        'title': "Заявка",
        "hashtag": "#Стажировка #Internship",
        "position_title": "Должность",
        "organization_name": "Компания",
        "requirements": "Требования",
        "duties": "Обязанности",
        "conditions": "Условия",
        "address": "Локация",
        "salary": "Оплата",
        "contact": "Контакты",
        "additional_info": "Дополнительно",
    },
    "kaa": {
        'title': "Soraw",
        "hashtag": "#Ámeliyat #Стажировка",
        "position_title": "Lawazım",
        "organization_name": "Mekeme",
        "requirements": "Talaplar",
        "duties": "Wazıypalar",
        "conditions": "Shárayatlar",
        "address": "Mánzil",
        "salary": "Tólem",
        "contact": "Baylanıs",
        "additional_info": "Qosımsha",
    },
    "uzb": {
        'title': "Ariza",
        "hashtag": "#Amaliyot #Стажировка",
        "position_title": "Lavozim",
        "organization_name": "Tashkilot",
        "requirements": "Talablar",
        "duties": "Vazifalar",
        "conditions": "Sharoitlar",
        "address": "Manzil",
        "salary": "To‘lov",
        "contact": "Aloqa",
        "additional_info": "Qo‘shimcha",
    },
    "kaz": {
        'title': "Өтініш",
        "hashtag": "#Тағылымдама #Стажировка",
        "position_title": "Лауазым",
        "organization_name": "Компания",
        "requirements": "Талаптар",
        "duties": "Міндеттер",
        "conditions": "Шарттар",
        "address": "Мекенжай",
        "salary": "Төлем",
        "contact": "Байланыс",
        "additional_info": "Қосымша",
    },
    "kgz": {
        'title': "Өтүнүч",
        "hashtag": "#Такшалма #Стажировка",
        "position_title": "Кызмат орду",
        "organization_name": "Мекеме",
        "requirements": "Талаптар",
        "duties": "Милдеттер",
        "conditions": "Шарттар",
        "address": "Жайгашкан жери",
        "salary": "Төлөм",
        "contact": "Байланыш",
        "additional_info": "Кошумча",
    },
    "tjk": {
        'title': "Дархост",
        "hashtag": "#Таҷрибаомӯзӣ #Стажировка",
        "position_title": "Мансаб",
        "organization_name": "Ширкат",
        "requirements": "Талабот",
        "duties": "Уҳдадориҳо",
        "conditions": "Шароит",
        "address": "Ҷойгиршавӣ",
        "salary": "Музд",
        "contact": "Тамос",
        "additional_info": "Маълумоти иловагӣ",
    },
    "aze": {
        'title': "Müraciət",
        "hashtag": "#Təcrübə #Internship",
        "position_title": "Vəzifə",
        "organization_name": "Şirkət",
        "address": "Yerləşmə",
        "requirements": "Tələblər",
        "duties": "Öhdəliklər",
        "conditions": "Şərtlər",
        "salary": "Ödəniş",
        "contact": "Əlaqə",
        "additional_info": "Əlavə",
    },
    "tkm": {
        'title': "Arza",
        "hashtag": "#HünärOkuwy #Стажировка",
        "position_title": "Wezipe",
        "organization_name": "Kompaniýa",
        "requirements": "Talaplar",
        "duties": "Borçlar",  
        "conditions": "Şertler",
        "address": "Ýerleşýän ýeri",
        "salary": "Töleg",
        "contact": "Habarlaşmak",
        "additional_info": "Goşmaça",
    },
}

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: Internship) -> TgPost:
    d = LABELS.get(lang_code, LABELS["eng"])
    lines = [
        f"{d['hashtag']}\n",
        f"👨‍💼 <b>{d['position_title']}</b>: {esc(post.position_title)}",
    ]
    if post.organization_name:
        lines.append(f"🏛 <b>{d['organization_name']}</b>: {esc(post.organization_name)}")
    lines += [
        f"📌 <b>{d['requirements']}</b>: {esc(post.requirements)}",
        f"⚙️ <b>{d['duties']}</b>: {esc(post.duties)}"
    ]
    if post.conditions:
        lines.append(f"⚖️ <b>{d['conditions']}</b>: {esc(post.conditions)}")
    lines += [
        f"📍 <b>{d['address']}</b>: {esc(post.address)}",
        f"💰 <b>{d['salary']}</b>: {esc(post.salary)}",
        f"☎️ <b>{d['contact']}</b>: {esc(post.contact)}",
    ]
    if post.additional_info:
        lines.append(f"📎 <b>{d['additional_info']}</b>: {esc(post.additional_info)}")
    result = "\n".join(lines)
    return TgPost(text=result)

async def get_vacancy_group_format(post: Internship, lang_code: str = "kaa") -> str:
    d = LABELS.get(lang_code, LABELS["kaa"])
    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"
    group_version = await get_vacancy_channel_format(lang_code=lang_code, post=post)
    return header + loc + group_version.text