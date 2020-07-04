from dataclasses import dataclass
from typing import List, Union

from typing_extensions import Literal

class Dictable(object):
    base = {}

    @property
    def dictionary(self):
        return self.base


class FatherOfAQB(Dictable):
    base = {}

    def __init__(self, base=None):
        if base: self.base = base


class Action(FatherOfAQB):
    @classmethod
    def unsetCustomField(cls, field: str):
        base = {"action": "unset_field_value", "field_name": field}
        action = cls(base)
        return action

    @classmethod
    def setCustonField(cls, field: str, value):
        base = {"action": "set_field_value", "field_name": field, "value": value}
        return cls(base)


class QuickReply(FatherOfAQB):
    @classmethod
    def dynamicBlockQR(cls, url: str, method: str = 'post', payload=None):
        if payload is None:
            payload = {}
        base = {
            "type": "dynamic_block_callback",
            "caption": "Dynamic content",
            "url": url,
            "method": method,
            "headers": {"x-header": "value"},
            "payload": payload,
        }
        return cls(base)


class Button(FatherOfAQB):
    @classmethod
    def urlButton(cls, url, text, webview_size: Literal['full', 'medium', 'compact'] = "full"):
        base = {
            "type": "url",
            "caption": text,
            "url": url,
            "webview_size": webview_size
        }
        return cls(base)

    @classmethod
    def callButton(cls, text, phone):
        base = {
            "type": "call",
            "caption": text,
            "phone": phone  # "+1 (555) 555-55-55"
        }
        return cls(base)

    @classmethod
    def nodeButton(cls, text, target, actions=None):
        if actions is None:
            actions = []
        base = {
            "type": "node",
            "caption": text,
            "target": target,
            "actions": [a.dictionary for a in actions]
        }
        return cls(base)

    @classmethod
    def flowButton(cls, text, target):
        base = {
            "type": "flow",
            "caption": text,
            "target": target
        }
        return cls(base)

    @classmethod
    def dynamicBlockButton(cls, text, url, method='post', headers=None, payload=None):
        if payload is None:
            payload = {}
        if headers is None:
            headers = {}
        base = {
            "type": "dynamic_block_callback",
            "caption": text,
            "url": url,
            "method": method,
            "headers": headers,
            "payload": payload
        }
        return cls(base)


class GalleryCard(Dictable):

    def __init__(self, title: str, subtitle: Union[str, List[str]], image_url: str, buttons: List[Button] = None,
                 action_url: str = None):
        self.title = title
        if subtitle:
            if isinstance(subtitle, list):
                self.subtitle = '\n'.join(subtitle)
            elif isinstance(subtitle, str):
                self.subtitle = subtitle
            else:
                raise TypeError
        else:
            self.subtitle = ''
        self.image_url = image_url
        if buttons is None:
            self.buttons = []
        else:
            self.buttons = buttons
        self.action_url = action_url

    @property
    def dictionary(self):
        base = {
            "title": self.title,
            "subtitle": self.subtitle,
            "image_url": self.image_url,
            "action_url": self.action_url,
            "buttons": [b.dictionary for b in self.buttons],
        }
        # if self.action_url is None:
        #     del base["action_url"]
        return base


# https://manychat.github.io/dynamic_block_docs/
class Message(Dictable):
    pass


class Gallery(Message):
    base = {
        "type": "cards",
        "elements": [
            {
                "title": "Card title",
                "subtitle": "งาน",
                "image_url": "https://manybot-thumbnails.s3.eu-central-1.amazonaws.com/ca/xxxxxxzzzzzzzzz.png",
                "action_url": "https://manychat.com",
                "buttons": [],
            }
        ],
        "image_aspect_ratio": "horizontal",
    }

    def __init__(self, cards: List[GalleryCard], *,
                 image_aspect_ratio: Literal['horizontal', 'square'] = "horizontal"):
        base = self.base
        base['elements'] = [x.dictionary for x in cards]
        base['image_aspect_ratio'] = image_aspect_ratio


class ImageMessage(Message):

    def __init__(self, image_url: str, buttons: List[Button] = None):
        self.image_url = image_url
        self.buttons = [] if buttons is None else buttons

    @property
    def dictionary(self):
        base = {
            "type": "image",
            "url": self.image_url,
            "buttons": self.buttons,
        }
        return base


class Text(Message):
    base = {
        "type": "text",
        "text": "simple text with button",
        "buttons": [
            {
                "type": "url",
                "caption": "External link",
                "url": "https://manychat.com",
            }
        ],
    }

    def __init__(self, text: Union[List[str], str], buttons: List[Button] = None):
        if buttons is None:
            buttons = []
        self.base["buttons"] = list(map(lambda x: x.dictionary, buttons))
        if isinstance(text, str):
            self.base["text"] = text
        elif isinstance(text, List):
            self.base["text"] = '\n'.join(text)


class Messages(Dictable):
    def __init__(self, messages: Union[List[Message], Message], actions=None,
                 quick_replies=None):
        if actions is None:
            actions = []
        if quick_replies is None:
            quick_replies = []
        if isinstance(messages, list):
            self.messages = messages
        else:
            self.messages = [messages]
        self.actions = actions
        self.quick_replies = quick_replies

    @property
    def dictionary(self):
        return {
            "version": "v2",
            "content": {
                "messages": [m.dictionary for m in self.messages],
                "actions": self.actions,
                "quick_replies": self.quick_replies
            }
        }


@dataclass
class ManychatUser:
    id_: int

    @classmethod
    def from_content(cls, content: dict):
        userId = content['id']
        return cls(userId)
