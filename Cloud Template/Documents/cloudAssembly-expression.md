어셈블리 표현식과 정규식은 다름.

표현식은 다음과 같은 리터럴 형식 지원

- 부울(true / false), 정수, 부동 소수점, String, null

조건

- == , != , < > , <= , >= 등
- && , || , !
- 조건부 패턴 사용: condition-expression?true-expression:false-expression

맵 구성

`${{'key1':'value1', 'key2':input.key2}}` 

어레이구성

`${['key1','key2']}`

예:

`${[1,2,3]}`

함수

구문:

`${함수(인수...)}`

예:

`${to_lower(resource.app.name)}`

함수

| **함수** | **설명** |
| --- | --- |
| abs(숫자) | 절대 숫자 값 |
| avg(어레이) | 숫자 어레이에서 모든 값의 평균을 반환 |
| base64_decode(문자열) | 디코딩된 base64 값을 반환 |
| base64_encode(문자열) | base64로 인코딩된 값을 반환 |
| ceil(숫자) | 인수 보다 크거나 같고 수학 정수와 동일한 최소(음의 무한대에 가장 가까움) 값을 반환 |
| contains(어레이, 값) | 어레이에 값이 포함되어 있는지 확인 |
| contains(문자열,값) | 문자열에 값이 포함되어 있는지 확인 |
| digest(값, 유형) | 지원되는 유형(md5, sha1, sha256, sha384, sha512)을 사용하여 값의 다이제스트를 반환 |
| ends_with(주체, 접미사) | 주체 문자열이 접미사 문자열로 끝나는지 확인 |
| filter_by(어레이, 필터) | 필터 작업을 통과한 어레이 항목만 반환합니다.
`filter_by([1,2,3,4], x => x >= 2 && x <= 3)`
`[2, 3]` 반환
`filter_by({'key1':1, 'key2':2}, (k,v) => v != 1)`
`[{"key2": 2}]` 반환 |
| floor(숫자) | 인수보다 작거나 같고 수학 정수와 동일한 최대(양의 무한대에 가장 가까움) 값을 반환 |
| format(형식, 값 ...) | Java [Class Formatter](https://docs.oracle.com/javase/8/docs/api/java/util/Formatter.html) 형식 및 값을 사용하여 형식이 지정된 문자열을 반환 |
| from_json(문자열) | json 문자열을 구문 분석 |
| join(어레이, 구분 기호) | 구분 기호로 문자열 어레이를 연결하고 문자열을 반환 |
| json_path(값, 경로) | [XPath for JSON](https://goessner.net/articles/JsonPath/)을 사용하여 값에 대해 경로를 평가 |
| keys(맵) | 맵의 키를 반환 |
| length(어레이) | 어레이 길이를 반환 |
| length(문자열) | 문자열 길이를 반환 |
| map_by(어레이, 작업) | 작업이 적용된 각 어레이 항목을 반환합니다.
`map_by([1,2], x => x * 10)`
`[10, 20]` 반환
`map_by([1,2], x => to_string(x))`
`["1", "2"]` 반환
`map_by({'key1':1, 'key2':2}, (k,v) => {k:v*10})`
`[{"key1":10},{"key2":20}]` 반환 |
| map_to_object(어레이, 키 이름) | 다른 어레이의 값과 쌍으로 구성된 지정된 키 이름의 key:value 쌍의 어레이를 반환합니다.
`map_to_object(resource.Disk[*].id, "source")`
디스크 ID 문자열과 쌍으로 구성된 source라는 키 필드가 있는 key:value 쌍의 어레이를 반환합니다.
다음
`map_by(resource.Disk[*].id, id => {'source':id})`
식은 동일한 결과를 반환합니다. |
| matches(문자열, 정규식) | 문자열이 정규 표현식과 일치하는지 확인 |
| max(어레이) | 숫자 어레이에서 최대값을 반환 |
| merge(맵, 맵) | 병합된 맵을 반환 |
| min(어레이) | 숫자 어레이에서 최소값을 반환 |
| not_null(어레이) | null이 아닌 첫 번째 항목을 반환 |
| now() | 현재 시간을 ISO-8601형식으로 반환 |
| range(시작, 중지) | 시작 번호로 시작하여 중지 번호 바로 앞에서 끝나는, 1씩 증가하는 일련의 숫자를 반환합니다. |
| replace(문자열, 대상, 교체) | 대상 문자열을 포함하는 문자열을 대상 문자열로 교체 |
| reverse(어레이) | 어레이 항목의 방향을 반전 |
| slice(어레이, 시작, 끝) | 시작 인덱스에서 끝 인덱스까지 어레이 조각을 반환 |
| split(문자열, 분 기호) | 구분 기호로 문자열을 분할하고 문자열 어레이를 반환 |
| starts_with(주체, 접두사) | 주체 문자열이 접두사 문자열로 시작하는지 확인 |
| substring(문자열, 시작, 끝) | 시작 인덱스에서 끝 인덱스까지 문자열의 하위 문자열을 반환 |
| sum(어레이) | 숫자 어레이에서 모든 값의 합계를 반환 |
| to_json(값) | 값을 json 문자열로 직렬화 |
| to_lower(문자열) | 문자열을 소문자로 변환 |
| to_number(문자열) | 문자열을 숫자로 구문 분석 |
| to_string(값) | 값의 문자열 표현을 반환 |
| to_upper(문자열) | 문자열을 대문자로 변환 |
| trim(문자열) | 앞뒤 공백 제거 |
| url_encode(문자열) | URL 인코딩 규격을 사용하여 문자열을 인코딩 |
| uuid() | 임의로 생성된 UUID를 반환 |
| values(맵) | 맵의 값을 반환 |
