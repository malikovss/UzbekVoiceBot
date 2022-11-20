import json
import logging
import os
from typing import Optional, Any

import aiohttp

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


common_voice = CommonVoice()
