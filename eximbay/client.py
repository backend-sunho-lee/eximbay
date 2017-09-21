import operator
import hashlib
import requests
from jinja2 import Template

class Eximbay(object):
    def __init__(self, eximbay_mid, eximbay_secret, eximbay_env='test'):
        self.eximbay_mid = eximbay_mid
        self.eximbay_secret = eximbay_secret

        if eximbay_env == 'test':
            self.eximbay_url = 'https://secureapi.test.eximbay.com'
        elif eximbay_env == 'prod':
            self.eximbay_url = 'https://secureapi.eximbay.com'

    def _fgkey(self, **kwargs):
        """
        fgkey는 가맹점과 Eximbay 사이에 전송되는 데이터의 유효성을 확인하기 위해 사용됩니다.

        :param kwargs: 모든 요청/응답 데이터
        :return: fgkey를 만들어 반환합니다.
        """
        # A : 모든 요청/응답 데이터의 key 값들을 기준으로 sorting
        data = sorted(kwargs.items(), key=operator.itemgetter(0))

        # 이렇게 쿼리스트링을 만드는 이유: 다른 라이브러리를 쓰면 한글이 깨져서 엑심베이가 싫어합니다.
        #! 더 좋은 대안이 있다면 알려주세요!
        params = ''
        for (key, value) in data:
            params += key + '=' + value + '&'
        params = params[0:-1]

        # B: secretkey와 A의 데이터를 “?”로 연결
        sp = self.eximbay_secret + '?' + params

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
        url = '{}/Gateway/BasicProcessor.krp'.format(self.eximbay_url)
        for key in ['statusurl', 'returnurl', 'ref', 'ostype', 'displaytype', 'paymethod', 'cur', 'amt', 'lang', 'shop', 'buyer', 'email', 'tel']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        kwargs['fgkey'] = self._fgkey(**kwargs)

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
        return template.render(reqUrl=url, data=kwargs)

    def refund(self, **kwargs):
        """
        엑심베이 환불 요청

        :param kwargs: 필수 요소들을 입력해야합니다. 굉장히 많습니다.
        :return:
        """
        url = '{}/Gateway/DirectProcessor.krp'.format(self.eximbay_url)
        for key in ['returnurl', 'refundtype', 'refundamt', 'ref', 'transid', 'refundid', 'reason', 'ostype', 'displaytype', 'paymethod', 'cur', 'amt', 'lang']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        res = requests.post(url, data=kwargs)
        return res.content

    def query(self, **kwargs):
        """
        엑심베이 결제 조회 요청

        :param kwargs: 필수 요소들을 입력해야합니다. 굉장히 많습니다.
        :return:
        """
        url = '{}/Gateway/DirectProcessor.krp'.format(self.eximbay_url)
        for key in ['returnurl', 'keyfield', 'ref', 'transid', 'cur', 'amt', 'lang']:
            if key not in kwargs:
                raise KeyError('Essential parameter is missing!: %s' % key)

        res = requests.post(url, data=kwargs)

        #: returnurl 없을 때 쿼리스트링으로 들어오는 응답을 바꾸는 방법
        from urllib.parse import parse_qs
        import json
        return json.dumps(parse_qs(res.text))
