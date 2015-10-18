from base64 import b64decode, urlsafe_b64decode
from collections import UserDict
import re


class LinkHeader(UserDict):

    @staticmethod
    def from_str(str):
        link_header = LinkHeader()
        matches = re.findall('<(?P<url>.+?)>;\s+rel="(?P<rel>.+?)"+', str)
        for match in matches:
            url, rel = match
            link_header[rel] = url
        return link_header

    def __str__(self):
        return ', '.join(['<{}>; rel="{}"'.format(url, name)
                          for name, url in self.items()])
