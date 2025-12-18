# eng, rus, kaa, uzb, kaz, kgz, tjk, aze, tkm
from fastapi import APIRouter

router = APIRouter(prefix="/languages", tags=['Languages list'])

@router.get("/")
async def get_languages_list():
    return [
        {
            'code': "eng",
            "official_name": "English"
        },
        {
            'code': "rus",
            "official_name": "Русский"
        },
        {
            'code': "uzb",
            "official_name": "Oʻzbekcha"
        },
        {
            'code': "kaz",
            "official_name": "Қазақша"
        },
        {
            'code': "kaa",
            "official_name": "Qaraqalpaqsha"
        },
        {
            'code': "kgz",
            "official_name": "Кыргызча"
        },
        {
            'code': "tjk",
            "official_name": "Тоҷикӣ"
        },
        {
            'code': "aze",
            "official_name": "Azərbaycan"
        },
        {
            'code': "tkm",
            "official_name": "Türkmençe"
        },
    ]