from typing import Optional, List, Dict, Any
from enum import IntEnum


class PollLayoutType(IntEnum):
    DEFAULT = 1


class PollMedia:
    def __init__(self, data: Dict[str, Any]):
        self.text: Optional[str] = data.get('text')
        self.emoji: Optional[Dict] = data.get('emoji')

    def to_dict(self) -> Dict[str, Any]:
        data = {}
        if self.text:
            data['text'] = self.text
        if self.emoji:
            data['emoji'] = self.emoji
        return data


class PollAnswer:
    def __init__(self, data: Dict[str, Any]):
        self.answer_id: int = data.get('answer_id', 0)
        self.poll_media: PollMedia = PollMedia(data.get('poll_media', {}))
        self.count: int = 0
        self.me_voted: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {'poll_media': self.poll_media.to_dict()}


class Poll:
    def __init__(self, data: Dict[str, Any], session=None, channel_id: str = None, message_id: str = None):
        self._session = session
        self._channel_id = channel_id
        self._message_id = message_id
        self._update(data)

    def _update(self, data: Dict[str, Any]):
        self.question: PollMedia = PollMedia(data.get('question', {}))
        self.answers: List[PollAnswer] = [PollAnswer(a) for a in data.get('answers', [])]
        self.expiry: Optional[str] = data.get('expiry')
        self.allow_multiselect: bool = data.get('allow_multiselect', False)
        self.layout_type: PollLayoutType = PollLayoutType(data.get('layout_type', 1))
        self.is_finalized: bool = data.get('results', {}).get('is_finalized', False)

        results = data.get('results', {})
        for answer_count in results.get('answer_counts', []):
            for answer in self.answers:
                if answer.answer_id == answer_count['id']:
                    answer.count = answer_count['count']
                    answer.me_voted = answer_count['me_voted']

    async def vote(self, answer_id: int) -> None:
        await self._session.rest.create_poll_answer(self._channel_id, self._message_id, answer_id)

    async def remove_vote(self, answer_id: int) -> None:
        await self._session.rest.delete_poll_answer(self._channel_id, self._message_id, answer_id)

    async def end(self) -> 'Poll':
        data = await self._session.rest.end_poll(self._channel_id, self._message_id)
        poll_data = data.get('poll', {})
        self._update(poll_data)
        return self

    async def fetch_voters(self, answer_id: int, limit: int = 25) -> List[Dict]:
        return await self._session.rest.get_poll_answer_voters(
            self._channel_id, self._message_id, answer_id, limit=limit
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': self.question.to_dict(),
            'answers': [a.to_dict() for a in self.answers],
            'expiry': self.expiry,
            'allow_multiselect': self.allow_multiselect,
            'layout_type': int(self.layout_type)
        }


class PollBuilder:
    def __init__(self, question: str, duration_hours: int = 24, allow_multiselect: bool = False):
        self._question = question
        self._duration = duration_hours
        self._multiselect = allow_multiselect
        self._answers: List[Dict] = []

    def add_answer(self, text: str, emoji: str = None) -> 'PollBuilder':
        answer: Dict[str, Any] = {'poll_media': {'text': text}}
        if emoji:
            answer['poll_media']['emoji'] = {'name': emoji}
        self._answers.append(answer)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            'question': {'text': self._question},
            'answers': self._answers,
            'duration': self._duration,
            'allow_multiselect': self._multiselect,
            'layout_type': 1
        }
