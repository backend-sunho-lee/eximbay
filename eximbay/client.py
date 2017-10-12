# -*- coding: utf-8 -*-
import operator
import hashlib
import requests
from jinja2 import Template
from urllib.parse import urlsplit, parse_qsl

class Eximbay(object):
    def __init__(self, exb_mid, exb_secret, exb_env='prod'):
        self.exb_mid = exb_mid
        self.exb_secret = exb_secret

        if exb_env == 'test':
            self.exb_url = 'https://secureapi.test.eximbay.com'
        elif exb_env == 'prod':
            self.exb_url = 'https://secureapi.eximbay.com'

    def make_querystring(self, **kwargs):
        """
        이렇게 쿼리스트링을 만드는 이유: 다른 라이브러리를 쓰면 한글이 깨져서 엑심베이가 싫어합니다.
        더 좋은 대안이 있다면 알려주세요!

        :param kwargs:
        :return:
        """
        # 모든 요청/응답 데이터의 key 값들을 기준으로 sorting
        data = sorted(kwargs.items(), key=operator.itemgetter(0))

        params = ''
        for (key, value) in data:
            params += key + '=' + str(value) + '&'
        params = params[0:-1]
        return params

    def _fgkey(self, **kwargs):
        """
        fgkey는 가맹점과 Eximbay 사이에 전송되는 데이터의 유효성을 확인하기 위해 사용됩니다.

        :param kwargs: 모든 요청/응답 데이터
        :return: fgkey를 만들어 반환합니다.
        """
        params = self.make_querystring(**kwargs)

        # B: secretkey와 A의 데이터를 “?”로 연결
        sp = self.exb_secret + '?' + params

        # C: B의 결과를 SHA256 함수를 통해 Hashing 하여 생성합니다.
        # SHA256를 위해 bytes 변환 시, character set은 반드시 UTF-8로 사용
        fgkey = hashlib.sha256(sp.encode('utf-8')).hexdigest()
        return fgkey

    def payment(self, **kwargs):
        """
        엑심베이에 결제 요청

        :param kwargs: 필수 요소들을 입력해야합니다. 굉장히 많습니다.
        :return: 엑심베이가 제공하는 결제 페이지로 넘어갑니다.
        """
        data = {
            'ver': '230', # 연동버전
            'txntype': 'PAYMENT', # 거래 타입
            'charset': 'UTF-8',
            'mid': self.exb_mid
        }

        url = '{}/Gateway/BasicProcessor.krp'.format(self.exb_url)
        for key in ['statusurl', 'returnurl', 'ref', 'ostype', 'displaytype', 'paymethod', 'cur', 'amt', 'lang', 'buyer', 'email']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        data.update(kwargs)
        data['fgkey'] = self._fgkey(**data)

        template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        </head>
        <body leftmargin="0" topmargin="0" align="center" onload="javascript:document.regForm.submit();">
        {% if data %}
          <form name="regForm" method="post" action="{{ reqUrl }}">
          {% for key, value in data.items() %}
            <input type="hidden" name="{{ key }}" value="{{ value }}" >
          {% endfor %}
          </form>
        {% else %}
          <h1>No Data!!!</h1>
        {% endif %}
        </body>
        </html>
        """)
        return template.render(reqUrl=url, data=data)

    def refund(self, **kwargs):
        """
        엑심베이 환불 요청

        :param kwargs: 필수 요소들을 입력해야합니다. 굉장히 많습니다.
        :return:
        """
        data = {
            'ver': '230', # 연동버전
            'txntype': 'REFUND', # 거래 타입
            'charset': 'UTF-8',
            'mid': self.exb_mid
        }

        url = '{}/Gateway/DirectProcessor.krp'.format(self.exb_url)
        for key in ['refundtype', 'refundamt', 'ref', 'transid', 'refundid', 'reason', 'ostype', 'displaytype', 'paymethod', 'cur', 'amt', 'lang']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        data.update(kwargs)
        res = requests.post(url, data=data)

        # res의 fgkey로 위조 검사하기

        return res.content

    def query(self, **kwargs):
        """
        응답값과 결제내역조회의 결과값을 비교하여 위조를 검사합니다.

        :param kwargs: 필수 요소들을 입력해야합니다. 굉장히 많습니다.
        :return:
        """
        data = {
            'ver': '230', # 연동버전
            'txntype': 'QUERY', # 거래 타입
            'charset': 'UTF-8',
            'mid': self.exb_mid
        }

        url = '{}/Gateway/DirectProcessor.krp'.format(self.exb_url)
        for key in ['ref', 'cur', 'amt']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        data.update(kwargs)
        data['fgkey'] = self._fgkey(**data)

        _res = requests.post(url, data=data)
        res = dict(parse_qsl(urlsplit(_res.text).path))

        if res['rescode'] != '0000':
            return False, res
        else:
            return True, res

    def is_paid(self):
        # 주문번호로 결제 상태를 조회합니다.
        pass