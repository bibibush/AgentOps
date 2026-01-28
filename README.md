# 지원자에게 무엇이든 물어봐! (백엔드) [진행중]

## 소개

> openai response API와 openai agents sdk를 기반으로, 사용자 질문에 맞는 답을 만들어주는 AI 에이전트 서비스를 구현했습니다.
>
> fastAPI로 백엔드 API 서버를 구성하고, 에이전트의 핵심 응답 로직은 openai response API로 처리하도록 설계했습니다.
>
> 클린 아키텍처를 적용해 비즈니스 로직, 외부 연동 로직, 실제 작업 로직, API 라우트 정의를 분리했고, 확장과 유지보수가 쉬운 구조를 목표로 했습니다.
>
> 배포는 docker 기반으로 컨테이너화하고, ec2 + cloudFront 환경에 GitHub Actions CI/CD로 자동 배포되도록 구성했습니다.

## 사용 기술

- python 3.13
- fastAPI
- openai response API
- uv
- docker
- ec2
- cloudFront

## 프로젝트 구조 (클린 아키텍처)

```
.
├─ api/                           # API 라우트 정의
├─ application/                  # 유스케이스 / 서비스 로직
│  └─ openai_usecases.py          # OpenAI 응답 유스케이스
├─ domain/                        # 도메인 모델 / 핵심 비즈니스 규칙
│  ├─ models.py                   # 공통 도메인 모델
│  ├─ monitor.py                  # 모니터링(확장용)
│  └─ openai_response/            # OpenAI 응답 도메인
│     ├─ models.py                # 요청/응답 모델
│     ├─ ports.py                 # 포트(인터페이스) 정의
│     └─ prompt.py                # 프롬프트/정책 정의
├─ infrastructure/                # 외부 연동 (OpenAI, DB 등)
│  └─ openai_response/            # OpenAI Response API 연동
│     └─ api_repository.py        # 외부 API 호출 레포지토리
├─ main.py                        # 앱 엔트리
├─ Dockerfile
├─ docker-compose.yml
└─ pyproject.toml

```

## 핵심 로직

<details>
  <summary><b>OpenAI Response API로 채팅(스트리밍) 구현</b></summary>

### 1) Domain: 요청 모델 + 포트(인터페이스) 정의

- 요청/응답 스키마와 기본 프롬프트를 `domain/openai_response`에 둡니다.
- 인프라가 어떤 방식으로든 교체될 수 있도록 `ports.py`에 Port를 정의합니다.

```py
# domain/openai_response/models.py
class OpenAIResponseAPIModel(BaseModel):
    model: str
    input: Union[List[Dict], str]
    instructions: Optional[str] = system_prompt
    stream: Optional[bool] = False
```

```py
# domain/openai_response/ports.py
class OpenAIResponseAPIPort(Protocol):
    async def create_response(self, model: str, input: Any, stream: bool, **kwargs) -> Any: ...
    async def output_response_stream(self, response: Any) -> AsyncGenerator[Any, None]: ...
```

### 2) Infrastructure: OpenAI Response API 연동 구현

- `AsyncOpenAI().responses.create(...)`로 실제 응답을 생성합니다.
- 스트리밍일 경우 `response.output_text.delta` 이벤트만 골라서 전파합니다.

```py
# infrastructure/openai_response/api_repository.py
response = await self.client.responses.create(
    model=model,
    input=input,
    stream=stream,
    **kwargs
)

async for event in response:
    if event.type == "response.output_text.delta":
        yield event.delta
```

### 3) Application: 유스케이스에서 흐름을 묶기

- 유스케이스는 `create_response` → `output_response_*` 순서로 조합합니다.
- 스트리밍은 AsyncGenerator로 chunk를 그대로 넘깁니다.

```py
# application/openai_usecases.py
response = await self.openai_repository.create_response(**request_data)
async for chunk in self.openai_repository.output_response_stream(response):
    yield chunk
```

### 4) API: FastAPI 라우트에서 SSE로 전달

- `/openai-response/sse`는 `data: {chunk}\\n\\n` 형태로 내려줍니다.

```py
# api/openai_response/router.py
async def event_generator():
    async for chunk in openai_usecase.generate_stream_response(ai_request=data):
        yield f"data: {chunk}\\n\\n"

return StreamingResponse(event_generator(), media_type="text/event-stream")
```

</details>

## 개선 사항

> 아래 항목은 다음 단계에서 개선할 예정입니다.

- MySQL 또는 PostgreSQL를 도입해 지난 대화 내용 저장 기능 추가
- agents sdk를 도입해 에이전트간의 오케스트레이션 관리 기능 및 MCP 사용 기능 추가
