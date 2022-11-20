import json
import logging
import os
import random
import re
from typing import Optional, Any

import aiohttp
import librosa
from speechbrain.pretrained import VAD

from main import BASE_DIR
from utils.helpers import authorization_token

logger = logging.getLogger(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/95.0.4638.69 Safari/537.36',
}

GET_TEXT_URL = 'https://common.uzbekvoice.ai/api/v1/uz/sentences'
SEND_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
VOICE_VOTE_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips/{}/votes'
SKIP_VOICE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_clips/{}'
SKIP_SENTENCE_URL = 'https://common.uzbekvoice.ai/api/v1/skipped_sentences/{}'
GET_VOICES_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips'
REPORT_URL = 'https://common.uzbekvoice.ai/api/v1/reports'
CLIPS_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/leaderboard'
VOTES_LEADERBOARD_URL = 'https://common.uzbekvoice.ai/api/v1/clips/votes/leaderboard'
RECORDS_STAT_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips/stats'
ACTIVITY_STAT_URL = 'https://common.uzbekvoice.ai/api/v1/uz/clips/voices'

SAMPLE_SENTENCES = [
    "Va qahvaxona egasi jarimaga solindi.",
    "Bu yerda tushunmovchilik bo‘lgan.",
    "O‘zbekiston boks federatsiyasi aniqlik kiritdi.",
    "O‘qituvchilarni norozi qilmanglar.",
    "Federal xavfsizlik xizmatiga havolalar bo‘lgan.",
    "Tajovuzkor qo‘lga olingan.",
    "Hattoki sirtqida o‘qiydigan talabalarga ham.",
    "Shveysariyada jaziramadan so‘ng qor yog‘di.",
    "Qo‘l uchun antiseptik vosita ham defitsit.",
    "Biz O‘zbekistonga qaytdik.",
    "Yoshlikni saqlab qolishni xohlaysizmi?",
    "Yunusoboddagi uyning tomi yondi .",
    "Umumiy texnik talablar.",
    "Bu bizning asosiy maqsadimiz.",
    "Yaqin Sharqqa kelganimdan xursandman.",
    "Yo‘l bo‘lmasa, yo‘lsiz yashaydi.",
    "Samsung Yangi yil sovg‘alarini ulashmoqda!.",
    "Buni foydali deb o‘ylamayman.",
    "Shulardan biri o‘z nihoyasiga yetdi.",
    "Yoki pochtachi sumkasi.",
    "I darajali Davlat adliya maslahatchisi.",
    "Bu qoyilmaqom jang bo‘ldi.",
    "Hosilning bozori chaqqon.",
    "Boshqa boradigan joyim qolmadi.",
    "Shunchaki izohlashni istamayman”, dedi Tramp.",
    "Bu tatuirovka, nakleyka emas.",
    "Erkak yengil jarohat olgani aytilmoqda.",
    "Bu meni ilhomlantiradi deb o‘ylardim.",
    "Ammo kirish yo‘lagida isiriq tutatildi.",
    "Haydovchi qo‘lga olindi.",
    "Ularda mutlaqo boshqa tushunchalar hukmron.",
    "Britaniya hukumat aloqalari markazi.",
    "Ammo xavfsizlik haqida ham unutmang!",
    "Ko‘ramiz”, deydi Messi.",
    "Iroqda Isroil bayrog‘i taqiqlandi.",
    "Qolgan murojaatlar nazoratga olinib, ijroga qaratildi.",
    "Ayblanuvchilarning yaqinlari esa bundan norozi.",
    "Iste’molchilarga tanlov imkoniyati berilishi kerak.",
    "Nutqni rejissor so‘zladi.",
    "Essiz, yoshligim husnbuzarlar bilan o‘tmoqda.",
    "Foydasidan zarari ko‘p bo‘lgan sabzavotlar.",
    "Aftidan muddat qisqaradi shekilli.",
    "Bunga o‘zgartishlar kiritilishi kerak.",
    "Sababi, o‘qish sentabrdan boshlanardi.",
    "Avstraliyalik dayver akula qurboni bo‘ldi.",
    "Buyuk Britaniyada noma’lum dengiz mavjudoti aniqlandi.",
    "Tekshirish natijalari ma'lum qilinmagan.",
    "Asosiysi telefonni uyda unutib qoldirmang.",
    "Ishtirokchilar taklifni ma’qulladi.",
    "Go‘dak kuyib qolib, vafot etdi.",
    "Kanada bosh vaziri Jastin Tryudo.",
    "Aynan nima sizning harakatingizni sekinlashtiradi?",
    "Ba’zan tush surtsa ham, qayrilmaydi.",
    "Bunga nimaning hisobidan erishamiz?",
    "Bizni ulardan qayerimiz kam?",
    "Qanday hayot kechirish esa sizning tanlovingiz.",
    "Toshkentda yakkakurash bo‘yicha musobaqa o‘tkazildi.",
    "Atrofda yantoq juda ko‘p.",
    "Yarfo Muhammadni chaqirib keldi.",
    "Ansandagi xotira mehrobi.",
    "Gumonlanuvchi keyinroq qo‘lga olindi.",
    "Biz to‘xtamasligimiz lozim.",
    "Yigitlar vaziyatni tushunib turibdi.",
    "Hozircha chaqaloqning yaqinlari topilmadi.",
    "Bu bemorlarga tasalli beradi.",
    "Soxta mahsulotlardan ehtiyot bo‘ling !!!",
    "Keyingi yoz ular uchrashib, tanishmoqchi.",
    "Javob bo‘lmagach, xonaga kirdim.",
    "Mevali va manzarali daraxtlar ekildi.",
    "Ijtimoiy tarmoqlardagi trendlar.",
    "Reytingda yana Vladimir Putin yetakchilik qildi.",
    "Buxoruddin Yusuf Habibiy.",
    "Kassir uning talabini bajardi.",
    "Hamma tarmoqlar tahlil qilinmoqda.",
    "Ayol otasini baribir olib ketgan.",
    "Ammo qizig‘i keyin boshlandi.",
    "Investitsiya bo‘lmasa, iqtisodiyot rivojlanmaydi.",
    "Bolalar hayajondan yig‘lab yubordi.",
    "Ikki xalq mutlaqo o‘xshamaydi.",
    "Saytda qo‘shiqning audiosi e’lon qilingan.",
    "Afsuski, oliy ma’lumotim yo‘q.",
    "U yerda to‘rt kishi yaralandi.",
    "Leo qoyilmaqom o‘yin ko‘rsatmoqda.",
    "Chunki endi hujjatini yangilashi kerak.",
    "Quyida ushbu maqola to‘lig‘icha berildi.",
    "Holat yuzasidan jinoyat ishi qo‘zg‘atildi.",
    "Hammaning xayolida shu muammo.",
    "Abror Tursunpo‘latov, boks murabbiyi",
    "Kichkintoylar uchun o‘yin maydoni.",
    "Shahar juda o‘zgarib ketibdi.",
    "Oilasini boqishi kerak.",
    "Natijada samolyot Bayrutga qo‘ngan.",
    "Orada bir mizg‘ib oldim.",
    "O‘sha yili sen tug‘ilgan eding.",
    "Odamning vahmi keladi.",
    "Iqtisodiyot va moliya vazirlari o‘zgardi.",
    "Ayol yaralangan va kasalxonaga yotqizilgan.",
    "Uchrashuvda Oston to‘liq harakat qildi.",
    "Endigi navbatda Buxoro turgani aytilmoqda.",
    "Bir yildan so‘ng, balki qishgachadir.",
    "Odatda, unchalik ham xavfli emas.",
    "Ish haqingizdan ko‘nglingiz to‘lmayaptimi?",
    "UzReport Parijga e’tibor qaratadi.",
    "O‘zbekistonda esdalik tangalar narxi tushdi.",
    "Mahalliy aholi uylaridan ko‘chirilmoqda.",
    "Bu protseduralarning barchasi bajarilganmi?",
    "Hozirgi kunda sud tergovi ketayapti.",
    "ham qo‘lga olingan”, deyiladi xabarda.",
    "Bu poytaxt uchun antirekord hisoblanadi.",
    "O‘ylashga qo‘rqadi odam.",
    "Boshqa tafsilotlar hozircha keltirilmayapti.",
    "Tadbirkorlar bozor buzilishidan norozi .",
    "Ayrim o‘ziga xosliklar bilan.",
    "Ammo siz ham bizni eshiting.",
    "O‘zbekistonda urfga kirmagan moda trendlari.",
    "Lekin biz ishlashda davom etdik.",
    "Bunda qanday ish tutiladi?",
    "Sharoitlar shaharnikidan aslo qolishmaydi.",
    "Kitob tumanida yashagan.",
    "Shu bois muvaffaqiyatsizlik kuzatilgan.",
    "Uzr so‘rayman”, dedi futbolchi.",
    "Mamlakatda milliy motam e’lon qilindi .",
    "Ekspertlarning tadqiqotlari davom etmoqda.",
    "Uydagi o‘zaro tortishuv janjalga aylanadi.",
    "Bu xuddi mehmonxonada yashashga o‘xshadi”.",
    "Gap faqat mashg‘ulotlarda emas.",
    "Shunga qo‘rqib yuribman.",
    "O‘zbekistonning Ukrainadagi elchixonasi binosi.",
    "U tortning ko‘rinishini yanada boyitadi.",
    "Ta’lim dasturlari nochor va sayoz.",
    "Windows’da xavfli zaiflik aniqlandi.",
    "Avstraliya aborigenlari bayrog‘i.",
    "Faqat shundagina futbolni rivojlantirish mumkin.",
    "Ulardan birini keltirmoqdamiz.",
    "Saharlikka mazali sho‘rva retsepti.",
    "Hozirda hayvonot bog‘i yopilgan.",
    "O‘zbekistonda dollar kursi yana ko‘tarildi.",
    "Chempionlar Ligasi yakunlari haqida.",
    "Seni foydang zararing tegmagani, deydilar.",
    "Reytingda Germaniya termasi peshqadam.",
    "Ashbaxer bu ayblovlarni rad etgan.",
    "Instagram’dagi mashhur tuxum yorila boshladi.",
    "Kulishni ham, yig‘lashni ham bilmaysan.",
    "Hayronman, aytishga so‘z yo‘q.",
    "Xo‘sh, ular qanchalik haq edi?",
    "Sizning duogo‘ylaringiz ko‘p.",
    "Ularga esda qolarli hissiyotlar yetishmaydi!",
    "Bu revansh jangiga qattiq tayyorlandim.",
    "Yarim kechasi nima qilib yuribsiz?",
    "Tongda turiboq, mo‘ljallangan ishlarga kirishing.",
]
INCORRECT_CLIPS_PATH = [
    "src/incorrect_clips/1.mp3",
    "src/incorrect_clips/2.mp3",
    "src/incorrect_clips/3.mp3",
    "src/incorrect_clips/4.mp3",
    "src/incorrect_clips/5.mp3",
    "src/incorrect_clips/6.mp3",
    "src/incorrect_clips/7.mp3",
    "src/incorrect_clips/8.mp3",
    "src/incorrect_clips/9.mp3",
    "src/incorrect_clips/10.mp3",
    "src/incorrect_clips/11.mp3",
    "src/incorrect_clips/12.mp3",
    "src/incorrect_clips/13.mp3",
    "src/incorrect_clips/14.mp3",
    "src/incorrect_clips/15.mp3",
    "src/incorrect_clips/16.mp3",
    "src/incorrect_clips/17.mp3",
    "src/incorrect_clips/18.mp3"
]


def is_local_clip_id(clip_id):
    return int(clip_id) >= 9999999000


def is_local_clip(clip):
    return is_local_clip_id(clip["id"])


def get_local_clip(index):
    real_index = int(index) - 9999999000 if is_local_clip_id(index) else int(index)
    path = INCORRECT_CLIPS_PATH[real_index]
    sentence = random.choice(SAMPLE_SENTENCES)
    return {
        "id": 9999999000 + real_index,
        "is_correct": False,
        "local_path": path,
        "sentence": {
            "text": sentence,
        },
    }


def get_random_incorrect_voice():
    return get_local_clip(random.randint(0, len(INCORRECT_CLIPS_PATH) - 1))


def check_if_audio_human_voice(audio):
    savedir = str(BASE_DIR / "src" / "pretrained_models" / "vad-crdnn-libriparty")
    aaa = VAD.from_hparams(source="speechbrain/vad-crdnn-libriparty", savedir=savedir)
    boundaries = aaa.get_speech_segments(audio)

    return boundaries


def get_audio_duration(audio_path):
    return librosa.get_duration(filename=audio_path)


def replace(text):
    return re.sub(
        r'(ch|sh)',
        'c',
        # replace spaces and punctuation
        re.sub(r'[^\w\s]', '',
               re.sub(r'([a-zA-Z])\1+', r'\1', text))
    )

def check_if_audio_is_short(audio_path, text):
    characters_per_second = 18
    audio_duration = get_audio_duration(audio_path)
    text_duration = len(replace(text)) / characters_per_second
    return audio_duration < text_duration


class CommonVoiceError(Exception):
    pass


class CommonVoice:
    BASE_URL = "https://common.uzbekvoice.ai/api/v1"

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def close(self):
        if self._session:
            await self._session.close()

    def _make_url(self, path: str):
        if not path.startswith('/'):
            path = "/" + path
        return self.BASE_URL + path

    async def _make_request(
            self, method: str,
            path: str,
            data: Any = None,
            headers: dict = None,
            error_message: str = None
    ):
        async with self.session.request(method, self._make_url(path), headers=headers, data=data) as response:
            if response.status == 204 or response.status == 200:
                return
            raise CommonVoiceError(error_message)

    async def send_text_voice(self, token, file_directory, text_id):
        if not os.path.exists(file_directory):
            logger.error(f"File not found {file_directory}")
        else:
            headers = {
                'sentence_id': text_id,
                'Content-Type': 'audio/ogg',
                'Authorization': token,
                **HEADERS,
            }
            with open(file_directory, 'rb') as data:
                await self._make_request(
                    'POST',
                    path='/uz/clips',
                    data=data,
                    headers=headers,
                    error_message='Error sending voice'
                )

    async def send_voice_vote(self, token, voice_id, is_valid):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            **HEADERS,
        }
        data = {'challenge': 'null', "isValid": is_valid}
        await self._make_request(
            'POST',
            path=f"/uz/clips/{voice_id}/votes",
            data=data,
            headers=headers,
            error_message='Error sending vote'
        )

    async def skip_voice(self, token, voice_id):
        headers = {
            'Authorization': token,
            **HEADERS,
        }
        await self._make_request(
            'POST',
            path=f"/skipped_clips/{voice_id}",
            headers=headers,
            error_message="Error skipping voice"
        )

    async def skip_sentence(self, token, sentence_id):
        headers = {
            'Authorization': token,
            **HEADERS,
        }
        await self._make_request(
            'POST',
            path=f"/skipped_sentences/{sentence_id}",
            headers=headers,
            error_message="Error skipping sentence"
        )

    async def report_function(self, token, kind, id_to_report, report_type):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': token,
            **HEADERS,
        }
        _report_types = {
            'report_1': 'offensive-language',
            'report_2': 'grammar-or-spelling',
            'report_3': 'different-language',
        }
        reason = _report_types.get(report_type) or 'difficult-pronounce'
        data = {"kind": kind, "id": id_to_report, "reasons": [reason]}
        await self._make_request(
            'POST',
            path='/reports',
            data=json.dumps(data),
            headers=headers,
            error_message='Error reporting'
        )

    async def handle_operation(self, token: str, operation: dict):
        voice_id, sentence_id = operation.get('voice_id'), operation.get('sentence_id')
        _methods = {
            'vote': self.send_voice_vote(token, voice_id, operation["command"] == 'accept'),
            'report_clip': self.report_function(token, 'clip', voice_id, operation["command"]),
            'skip_clip': self.skip_voice(token, voice_id),
            'report_sentence': self.report_function(token, 'sentence', sentence_id, operation["command"]),
            'skip_sentence': self.skip_sentence(token, sentence_id),
            'send_voice': self.send_text_voice(token, operation["file_directory"], sentence_id)
        }
        if operation['type'] in _methods:
            await _methods[operation['type']]
        raise CommonVoiceError("Unknown operation type")

    async def get_votes_leaderboard(self, token: str):
        headers = {
            'Authorization': token,
        }
        async with self.session.get(VOTES_LEADERBOARD_URL, headers=headers) as response:
            votes_leaderboard = await response.json()
            given_votes, votes_position = 0, 0
            for i in votes_leaderboard:
                if i['you'] is True:
                    given_votes = i['total']
                    votes_position = i['position'] + 1
        return given_votes, votes_position

    async def get_clips_leaderboard(self, token: str):
        headers = {
            'Authorization': token,
        }
        async with self.session.get(CLIPS_LEADERBOARD_URL, headers=headers) as response:
            clips_leaderboard = await response.json()
            recorded_clips, clips_position = 0, 0
            for i in clips_leaderboard:
                if i['you'] is True:
                    recorded_clips = i['total']
                    clips_position = i['position'] + 1
        return recorded_clips, clips_position

    async def get_sentence_to_read(self, tg_id, state):
        data = await state.get_data()
        if "sentences" not in data or len(data["sentences"]) == 0:
            headers = {
                'Authorization': await authorization_token(tg_id),
                **HEADERS,
            }
            async with self.session.get(GET_TEXT_URL, headers=headers, params={'count': '50'}) as get_request:
                response_json = await get_request.json()
                await state.update_data(sentences=response_json)
                return await self.get_sentence_to_read(tg_id, state)
        else:
            recorded_sentences = data["recorded_sentence_ids"] if "recorded_sentence_ids" in data else []
            sentences = data["sentences"]
            sentence = None
            for i in range(len(sentences)):
                sentence = sentences.pop()
                if sentence["id"] not in recorded_sentences:
                    break
                else:
                    sentence = None
            await state.update_data(sentences=sentences)
            if sentence is None:
                sentence = await self.get_sentence_to_read(tg_id, state)
            return sentence

    async def get_voice_to_check(self, tg_id, state, user):
        probability = user["verification_probability"]
        use_incorrect_clips = random.random() < probability
        if use_incorrect_clips:
            return get_random_incorrect_voice()

        data = await state.get_data()
        if "voices" not in data or len(data["voices"]) == 0:
            headers = {
                'Referer': 'https://common.uzbekvoice.ai/uz/listen',
                'Authorization': await authorization_token(tg_id),
                **HEADERS
            }
            async with self.session.get(GET_VOICES_URL, headers=headers, params={'count': '50'}) as get_request:
                response_json = await get_request.json()
                await state.update_data(voices=response_json)
                return await self.get_voice_to_check(tg_id, state, user)
        else:
            checked_voices = data["checked_voice_ids"] if "checked_voice_ids" in data else []
            voices = data["voices"]
            voice = None
            for i in range(len(voices)):
                voice = voices.pop()
                if voice["id"] not in checked_voices:
                    break
                else:
                    voice = None
            await state.update_data(voices=voices)
            if voice is None:
                voice = await self.get_voice_to_check(tg_id, state, user)
            return voice

    async def download_file(self, download_url, voice_id):
        file_directory = str(BASE_DIR / 'downloads' / f"{voice_id}.ogg")
        async with self.session.get(download_url) as get_voice:
            with open(file_directory, "wb") as file_stream:
                video_url_content = await get_voice.content.read()
                file_stream.write(video_url_content)

            return file_directory


common_voice = CommonVoice()
