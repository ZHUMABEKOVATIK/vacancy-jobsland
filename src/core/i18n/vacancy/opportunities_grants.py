from src.models.vacancy import OpportunitiesGrants
from src.core.i18n.vacancy.vacancy_types import TgPost

LABELS = {
    "eng": {
        'title': "Application",
        "contact": "Contact",
    },
    "rus": {
        'title': "Заявка",
        "contact": "Контакты",
    },
    "kaa": {
        'title': "Soraw",
        "contact": "Baylanıs",
    },
    "uzb": {
        'title': "Ariza",
        "contact": "Aloqa",
    },
    "kaz": {
        'title': "Өтініш",
        "contact": "Байланыс",
    },
    "kgz": {
        'title': "Өтүнүч",
        "contact": "Байланыш",
    },
    "tjk": {
        'title': "Дархост",
        "contact": "Алоқа",
    },
    "aze": {
        'title': "Müraciət",
        "contact": "Əlaqə",
    },
    "tkm": {
        'title': "Arza",
        "contact": "Aragatnaşyk",
    },
}

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: OpportunitiesGrants) -> TgPost:
    d = LABELS.get(lang_code, LABELS["eng"])

    text = (
        f"{post.content}\n\n"
        f"{d.get('contact')}"
    )
    return TgPost(text=text, photo_path=post.img_path)

async def get_vacancy_group_format(post: OpportunitiesGrants, lang_code: str = "kaa") -> str:
    d = LABELS.get(lang_code, LABELS["kaa"])

    header = f"# {d['title']} ID: {post.id}\n\n"

    # Локация
    loc = f"🌎 {esc(post.country.name) if post.country else ''}"
    if post.region_id and post.region:
        loc += f" | {esc(post.region.name)}"
    loc += "\n\n"
    text = (
        f"{post.content}\n\n"
        f"{d.get('contact')}: {post.contact}"
    )
    return header + loc + text