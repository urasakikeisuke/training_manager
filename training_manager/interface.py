"interface.py"

import os

try:
    from typing import Tuple, Union, Optional, Sequence, Dict, List, Any
except ImportError:
    from typing_extensions import Tuple, Union, Optional, Sequence, Dict, List, Any # type: ignore

from datetime import datetime, timedelta, timezone
from pathlib import Path

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.slack_response import SlackResponse


HeaderBlock_t = Dict[str, Union[str, Dict[str, Union[str, bool]]]]
BodyBlock_t = Dict[str, Union[str, List[Dict[str, str]]]]
ComposedBlock_t = List[Union[HeaderBlock_t, BodyBlock_t]]

class TrainingManager:
    def __init__(
        self,
        bot_token: str,
        user_id: str,
    ) -> None:
        self.client = WebClient(token=bot_token)

        self.user_id = user_id
        self.channel_id = self._get_channel_id()

        self._ts_holder: Dict[str, str] = {}

    def _get_channel_id(self) -> str:
        try:
            response: SlackResponse = self.client.conversations_open(users=self.user_id)
        except SlackApiError:
            raise ValueError(f"Cannot find channel name. Make sure `user_id` is valid") from None

        return response["channel"]["id"]

    def _get_header_block(self, text: str) -> HeaderBlock_t:
        block: HeaderBlock_t = {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": text,
                "emoji": True
            }
        }

        return block

    def _get_body_field(self, text: str) -> Dict[str, str]:
        return {"type": "mrkdwn", "text": text}

    def _get_body_block(self, fields: Sequence[Dict[str, str]]) -> BodyBlock_t:
        block: BodyBlock_t = {
            "type": "section",
            "fields": fields
        }

        return block

    def _get_body_blocks(self, fields_group: Sequence[Sequence[Dict[str, str]]]) -> BodyBlock_t:
        blocks = []
        for i, fields in enumerate(fields_group):
            if i != 0:
                blocks.append(self._get_divider_block())
            block: BodyBlock_t = {
                "type": "section",
                "fields": fields
            }
            blocks.append(block)

        return blocks

    def _get_footer_block(self, text: str) -> BodyBlock_t:
        block: BodyBlock_t = {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": text
                },
            ]
        }

        return block
    
    def _get_divider_block(self) -> Dict[str, str]:
        return {"type": "divider"}

    def _compose_blocks(self, blocks: Sequence[Any]) -> ComposedBlock_t:
        composed_block: ComposedBlock_t = []
        for block in blocks:
            if block is not None:
                composed_block.append(block)
        
        return composed_block

    def get_ts(self, id: str) -> Optional[str]:
        return self._ts_holder.get(id)
    
    def send_plain_message(self, message: str) -> Tuple[bool, str]:
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=message
            )
        except SlackApiError as e:
            return (False, e.response["error"])

        return (True, response["ts"])

    def send_rich_block(self, mobile_text: str, blocks: Sequence[Union[Dict[str, str], Optional[BodyBlock_t], Optional[HeaderBlock_t]]], 
                        ts: Optional[str] = None, reply_broadcast: Optional[bool] = None, icon_emoji: Optional[str] = None) -> Tuple[bool, str]:
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=mobile_text,
                blocks=self._compose_blocks(blocks),
                thread_ts=ts,
                reply_broadcast=reply_broadcast,
                icon_emoji=icon_emoji
            )
        except SlackApiError as e:
            return (False, e.response["error"])

        return (True, response["ts"])

    def send_file(self, path: Union[str, Path], title: Optional[str] = None, text: Optional[str] = None, ts: Optional[str] = None) -> Tuple[bool, str]:
        if isinstance(path, str):
            path = Path(path)
        elif isinstance(path, Path):
            pass
        else:
            raise TypeError(f"`path` expected `str` or `pathlib.Path` but got `{type(path).__name__}`")

        if not path.is_file():
            raise ValueError(f"Specified `path` is not valid file")

        try:
            response = self.client.files_upload(
                file=str(path),
                channels=self.channel_id,
                title=title,
                initial_comment=text,
                thread_ts=ts
            )
        except SlackApiError as e:
            return (False, e.response["error"])

        return (True, response["ts"])

    def send_training_start(self, id: str, optionals: Optional[Sequence[dict]] = None) -> Tuple[bool, str]:
        header_block = self._get_header_block(f"学習開始 --- {id}")
        mobile_text = f"{id}の学習を開始しました"

        divider_block = self._get_divider_block()

        body_groups = []
        if optionals is not None:
            for optional in optionals:
                body_fields = []
                for i, (key, value) in enumerate(optional.items()):
                    if i > 9: break
                    body_fields.append(self._get_body_field(f"*{key}:* \n{value}"))
                body_groups.append(body_fields)

        body_blocks = self._get_body_blocks(body_groups)

        ts = self._ts_holder.get(f"{id}")

        result, ts_or_error = self.send_rich_block(mobile_text, [header_block, divider_block, *body_blocks], ts)

        if not result:
            return (False, ts_or_error)

        if ts is None:
            self._ts_holder[f"{id}"] = ts_or_error

        return (True, "")

    def send_progress(self, id: str, optionals: Optional[Sequence[dict]] = None) -> Tuple[bool, str]:
        header_block = self._get_header_block(f"途中経過 --- {id}")
        mobile_text = f"{id}の途中経過です"

        divider_block = self._get_divider_block()

        body_groups = []
        if optionals is not None:
            for optional in optionals:
                body_fields = []
                for i, (key, value) in enumerate(optional.items()):
                    if i > 9: break
                    body_fields.append(self._get_body_field(f"*{key}:* \n{value}"))
                body_groups.append(body_fields)

        body_blocks = self._get_body_blocks(body_groups)

        ts = self._ts_holder.get(f"{id}")

        result, ts_or_error = self.send_rich_block(mobile_text, [header_block, divider_block, *body_blocks], ts)

        if not result:
            return (False, ts_or_error)

        if ts is None:
            self._ts_holder[f"{id}"] = ts_or_error

        return (True, "")

    def send_error(self, id: str, optional: dict, reply_broadcast: bool = True) -> Tuple[bool, str]:
        header_block = self._get_header_block(f"エラーが発生しました --- {id}")
        mobile_text = f"{id}でエラーが発生しました"

        divider_block = self._get_divider_block()

        body_fields = []
        if optional is not None:
            for key, value in optional.items():
                body_fields.append(self._get_body_field(f"*{key}:* {value}"))

        body_block = self._get_body_block(body_fields)

        ts = self._ts_holder.get(f"{id}")

        result, ts_or_error = self.send_rich_block(mobile_text, [header_block, divider_block, body_block], 
                                                   ts, reply_broadcast, icon_emoji=":warning:")

        if not result:
            return (False, ts_or_error)

        if ts is None:
            self._ts_holder[f"{id}"] = ts_or_error

        return (True, "")

    def send_result(self, id: str, optional: dict) -> Tuple[bool, str]:
        header_block = self._get_header_block(f"学習終了 --- {id}")
        mobile_text = f"{id}の学習が終了しました"

        divider_block = self._get_divider_block()

        body_fields = []
        for key, value in optional.items():
            body_fields.append(self._get_body_field(f"*{key}* : {value}"))
        
        body_block = self._get_body_block(body_fields)

        ts = self._ts_holder.get(f"{id}")

        result, ts_or_error = self.send_rich_block(mobile_text, [header_block, divider_block, body_block], ts)

        if not result:
            return (False, ts_or_error)

        if ts is None:
            self._ts_holder[f"{id}"] = ts_or_error

        return (True, "")
    