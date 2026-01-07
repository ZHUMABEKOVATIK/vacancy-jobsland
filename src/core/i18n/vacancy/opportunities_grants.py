from src.models.vacancy import OpportunitiesGrants
from src.core.i18n.vacancy.vacancy_types import TgPost
from src.core.i18n.vacancy.converter import read_json_file

def esc(s: str | None) -> str:
    return (s or "").strip()

async def get_vacancy_channel_format(lang_code: str, post: OpportunitiesGrants) -> TgPost:
    LABELS_JSON = await read_json_file("./i18n_jsons/opportunities_grants.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["eng"])

    text = (
        f"{post.content}\n\n"
        f"{d.get('contact')}"
    )
    return TgPost(text=text, photo_path=post.img_path)

async def get_vacancy_group_format(post: OpportunitiesGrants, lang_code: str = "kaa") -> str:
    LABELS_JSON = await read_json_file("./i18n_jsons/opportunities_grants.json")
    d = LABELS_JSON.get(lang_code, LABELS_JSON["kaa"])

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