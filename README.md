# eximbay
Eximbay API with python. Python 사용자를 위한 엑심베이 REST API 연동 모듈입니다.

- 이용 중 발생한 문제에 대해 책임지지 않습니다.
- 엑심베이에서 제공하는 문서와 예제를 보고 만들었습니다.






## 설치
> 패키지화 할 예정
>
> 지금은 eximbay 폴더를 다운받아 사용하실 곳에서 import하여 써주세요.





## 기능

1. 결제
2. 환불
3. 결제상태 확인






## 사용법
> 아래의 data들은 필수 파라미터이며 추가할 수 있는 파라미터가 많습니다. 엑심베이에서 제공하는 문서를 보고 자유롭게 추가 가능합니다.

### 준비
사용하기 위해 객체를 만듭니다
```python
from eximbay import Eximbay

eximbay = Eximbay(exb_mid='{eximbay에서 할당한 가맹점 아이디}', exb_secret='{eximbay에서 할당한 시크릿}', exb_env='test')
# 테스트일 때만 exb_env='test'로 설정해주세요. 상용시에는 입력할 필요 없음
# 테스트용 정보는 아래에 따로 적어놨습니다.
```





### 결제

결제를 진행합니다.

```python
data = {
    #: 가맹점이 입력해야 할 정보
    'statusurl': 'http://{가맹점 도메인}/pay/status',
    # localhost로 설정하면 안됩니다. 결제 완료 시 Back-end 방식으로 Eximbay 서버에서 statusurl에 지정된 가맹점 페이지를 Back-end로 호출하여 파라미터를 전송
    # 브라우저에서 호출되지 않으므로, 스크립트, 쿠키, 세션 사용 불가.
    # statusurl은 중복해서 호출될 수 있으므로, 주문이 중복 처리되지 않도록 처리하여 주시기 바랍니다.

    'returnurl': 'http://localhost:5000/pay/return',
    # 결제 결과 확인화면에서 사용자가 결제창을 종료 할 경우 호출되는 가맹점 페이지
    # returnurl은 고객 브라우저 기반으로 동작하므로, 브라우저 강제 종료 시, 호출되지 않을 수 있습니다.

    'shop': '가맹점 이름',  # 상점명(가맹점명과 다른 경우 사용)
    'ref': 'order id', # 가맹점에서 만든 주문 번호
    # 가맹점에서 Transaction을 구분할 유일한 값으로 거래 실패 시에도 새로운 값으로 셋팅 요망
    # ref의 중복은 허용되어 있으며, ref에 따른 중복결제 방지를 원하는 경우, 엑심베이에 별도로 문의하여 주시기 바랍니다.

    'ostype': '', # P: pc version(기본값), M: mobile
    'displaytype': '', # P: popup(기본값) I: iframe(layer), R: page redirect
    'lang': 'KR', # 기본값: EN. 결제정보 언어타입 (Appendix B 참고)
    'paymethod': '', # 결제수단 코드 (문서 Appendix C 참고). 결제수단이 지정된 경우, 해당 결제 수단 페이지로 바로 이동

    'cur': 'USD', # 지원 통화 문서 Appendix B 참고
    'amt': '100',

    #: 고객이 입력해야 할 정보
    'buyer': 'Buyer', # 결제자명(실명사용요망)
    'email': 'email@email.com',
    'tel': '1234-5678', # 결제자 연락처
}

try:
    eximbay.payment(**data)
except Eximbay.ResponseError as e:
    # 응답 에러 처리
    pass
```

이를 실행하면 고객에게 결제 페이지가 보여집니다.
고객이 결제를 완료하면 returnurl이 고객에게 보여지고, statusurl에 결제 결과가 응답으로 들어옵니다.
statusurl로 들어온 값으로 DB작업 및 결제 프로세스 처리합니다.
statusurl을 '결제상태 확인'하는 기능이 있는 url로 설정하고 DB에 결제 정보를 저장하는 것을 추천합니다.





### 환불

결제를 취소합니다.

```python
data = {
    'returnurl': 'http://localhost:5000/pay/return', # 선택 옵

    'lang': 'KR',  # 기본값: EN. 결제정보 언어타입 (Appendix B. 참고)

    'ref': 'order id', # 가맹점에서 만든 주문 번호
    'transid': '',  # 결제사 거래 아이디
    'cur': 'USD',
    'amt': '100',
    'balance': '',
    # 원 승인 금액 – 합(환불금액). balance 가 0인 경우, 전체 환불된 거래입니다.
    # 값이 있는 경우만 체크한다.

    'refundtype': 'F',  # F: Fully, P: Partial. 전체 환불인지 부분 환불인지 설정
    'refundid': 'refund20170919202020', # 환불 요청에 대한 유일한 값으로 가맹점에서 생성. 모든 요청데이터의 refundid는 Unique 해야 합니다.
    'refundamt': '100', # 환불 요청 금액. refundamt가 정의되지 않은 경우, refundtype=F면, transid에 해당하는 승인 거래 총 금액을 환불처리 합니다.
    'reason': '',  # 환불사유
}

try:
    res = eximbay.payment(**data)
    # returnurl 입력하지 않은 경우, res로 환불 결과가 json형태로 나옵니다.
    # 입력한 경우는 res가 오지않고 바로 returnurl로 넘어갑니다. '결제상태 확인' 기능으로 연결하는 것을 추천합니다.
except Eximbay.ResponseError as e:
    # 응답 에러 처리
    pass
```





### 결제 확인

```python
status = eximbay.is_paid(ref='주문번호')
```
결제 결과는 아래의 네 종류가 있습니다.
- 정상매출 : SALE (매출 확정)
- 승인거래 : AUTH (매출 미확정, Capture시 매출 확정)
- 주문등록 : REGISTERED (매출 미확정, 입금통지 시 매 출 확정)
- 거래없음 : NONE






## 테스트시 필요한 정보들

- mid : 1849705C64

- secretkey : 289F40E6640124B2628640168C3C5464

- 테스트용 카드 정보
    - Card Type : VISA
    - Card No : 4111 1111 1111 1111
    - Expiry Date : 12/20
    - CVV : 123





## Review


회사에서 제공하는 문서 전체를 분석하고, 하나씩 시도해보고 문의하면서 만든 결과물입니다.

기존에 관련 API가 전혀 없던 상황에서 도전해볼 수 있는 기회를 얻어서 좋았습니다.






### Thanks to

- @psy2848048님의 제안으로 만들게 되었습니다. 좋은 제안해주셔서 감사합니다.

- KRP의 김종민님의 도움을 받아 만들었습니다. 매번 친절한 답장해주셔서 감사합니다.
