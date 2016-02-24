"""Henson-Twitter."""

import base64
from hashlib import sha1
import hmac
import json
import os
from pkg_resources import DistributionNotFound, get_distribution
from random import random
import time
from urllib.parse import quote, urlsplit, urlunsplit

import aiohttp
from henson import Extension

__all__ = ('Twitter',)

try:
    dist = get_distribution('henson_twitter')
    if not __file__.startswith(os.path.join(dist.location, 'henson_twitter')):
        raise DistributionNotFound
except DistributionNotFound:
    __version__ = 'development'
else:
    __version__ = dist.version


class Twitter(Extension):
    """An interface to consumer from Twitter."""

    REQUIRED_SETTINGS = (
        'TWITTER_CONSUMER_KEY',
        'TWITTER_CONSUMER_SECRET',
        'TWITTER_FILTER',
        'TWITTER_OAUTH_TOKEN',
        'TWITTER_OAUTH_TOKEN_SECRET',
    )

    def __init__(self, app=None):  # NOQA
        if app:
            self.init_app(app)

    def consumer(self):  # NOQA
        return Consumer(self.app)

    def init_app(self, app):  # NOQA
        super().init_app(app)

        app.consumer = self.consumer()


class Consumer:
    def __init__(self, app):
        self.app = app

        self._session = aiohttp.ClientSession()
        self.app.teardown(self._disconnect)

        self._response = None

        self._chunks = []

    async def read(self):
        if self._response is None:
            await self._connect()

        CHUNK_SIZE = 100
        while True:
            chunk = await self._response.content.read(CHUNK_SIZE)
            if not chunk:
                break

            chunk = chunk.decode('utf-8')

            if '\r' in chunk:
                end, chunk = chunk.split('\r')
                self._chunks.append(end)
                tweet = ''.join(self._chunks)

                self._chunks = [chunk]
                break

            self._chunks.append(chunk)

        return json.loads(tweet)

    async def _connect(self):
        self._signature = HmacSha1Signature()
        params = {
            'oauth_consumer_key': self.app.settings['TWITTER_CONSUMER_KEY'],
            'oauth_nonce': sha1(str(random()).encode('ascii')).hexdigest(),
            'oauth_signature_method': self._signature.name,
            'oauth_timestamp': int(time.time()),
            'oauth_version': '1.0',
            'oauth_token': self.app.settings['TWITTER_OAUTH_TOKEN'],
        }

        params.update(self.app.settings['TWITTER_FILTER'])

        params['oauth_signature'] = self._signature.sign(
            self.app.settings['TWITTER_CONSUMER_SECRET'],
            'POST',
            'https://stream.twitter.com/1.1/statuses/filter.json',
            oauth_token_secret=self.app.settings['TWITTER_OAUTH_TOKEN_SECRET'],
            **params,
        )

        self._response = await self._session.post(
            'https://stream.twitter.com/1.1/statuses/filter.json',
            params=params,
        )

    async def _disconnect(self, app):
        if self._response is not None:
            await self._response.release()
        await self._session.close()


class HmacSha1Signature():
    """HMAC-SHA1 signature-method."""

    name = 'HMAC-SHA1'

    def sign(self, consumer_secret, method, url, oauth_token_secret=None, **params):  # NOQA
        """Create a signature using HMAC-SHA1."""
        params = "&".join("%s=%s" % (k, quote(str(value), '~'))
                          for k, value in sorted(params.items()))
        method = method.upper()
        url = self._remove_qs(url)

        signature = b"&".join(map(self._escape, (method, url, params)))

        key = self._escape(consumer_secret) + b"&"
        if oauth_token_secret:
            key += self._escape(oauth_token_secret)

        hashed = hmac.new(key, signature, sha1)
        return base64.b64encode(hashed.digest()).decode()

    @staticmethod
    def _escape(s):
        """URL escape a string."""
        bs = s.encode('utf-8')
        return quote(bs, '~').encode('utf-8')

    @staticmethod
    def _remove_qs(url):
        """Remove query string from an URL."""
        scheme, netloc, path, _, fragment = urlsplit(url)

        return urlunsplit((scheme, netloc, path, '', fragment))
