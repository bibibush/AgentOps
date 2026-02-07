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
- sqlalchemy + alembic
- mysql
- openai response API
- uv
- docker
- ec2
- cloudFront

## 프로젝트 구조 (클린 아키텍처)

```
.
├─ api/                              # API 라우트 정의
│  ├─ router.py                       # 라우터 통합 (openai + session)
│  ├─ openai_response/
│  │  └─ router.py                    # OpenAI 응답 엔드포인트 (text, json, sse)
│  └─ session/
│     └─ router.py                    # 세션/유저 관리 엔드포인트
├─ application/                      # 유스케이스 / 서비스 로직
│  ├─ openai_usecases.py              # OpenAI 응답 유스케이스 (메시지 저장 포함)
│  └─ session_usecases.py             # 세션 생성·삭제·조회 유스케이스
├─ domain/                           # 도메인 모델 / 핵심 비즈니스 규칙
│  ├─ models.py                       # 공통 도메인 모델 (Session, ChatMessage, User, ResponseAPI)
│  ├─ ports.py                        # 범용 DB 포트 (MyDBPort[T])
│  ├─ parser.py                       # SSE 데이터 포맷터
│  ├─ monitor.py                      # 모니터링 (확장용)
│  └─ openai_response/                # OpenAI 응답 도메인
│     ├─ models.py                    # 요청/응답 모델
│     ├─ ports.py                     # 포트(인터페이스) 정의
│     └─ prompt.py                    # 프롬프트/정책 정의
├─ infrastructure/                   # 외부 연동 (OpenAI, DB 등)
│  ├─ db/                             # 데이터베이스 연동
│  │  ├─ __init__.py                  # DB 모듈 초기화
│  │  ├─ base.py                      # Async SQLAlchemy 엔진 + 세션 팩토리
│  │  └─ models.py                    # ORM 모델 (UserORM, SessionORM, ChatMessageORM)
│  ├─ mydb_repository.py              # 범용 DB 레포지토리 (MyDBRepository[T])
│  └─ openai_response/                # OpenAI Response API 연동
│     └─ api_repository.py            # 외부 API 호출 레포지토리
├─ alembic/                          # DB 마이그레이션
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions/                       # 마이그레이션 스크립트
├─ main.py                           # 앱 엔트리
├─ alembic.ini                       # Alembic 설정
├─ Dockerfile
├─ docker-compose.yml                 # 앱 + MySQL 서비스 정의
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

<details>
  <summary><b>세션 관리 및 과거 대화 내용 저장 구현</b></summary>

### 1) Domain: 도메인 모델 + 범용 DB 포트 정의

- `domain/models.py`에 `Session`, `ChatMessage`, `User` 모델을 정의합니다.
- `domain/ports.py`에 제네릭 `MyDBPort[T]`를 두어, 어떤 ORM 엔티티든 동일한 인터페이스로 다룰 수 있게 합니다.

```py
# domain/models.py
class Session(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: Optional[str]
    token: Optional[str]
    messages: list['ChatMessage'] = []
    created_at: datetime

class ChatMessage(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    message: str
    session_id: int
    created_at: datetime
```

```py
# domain/ports.py
class MyDBPort(Protocol[T]):
    async def add(self, entity: T) -> T: ...
    async def get_by_id(self, entity_id: int) -> Optional[T]: ...
    async def filter_by(self, **kwargs) -> List[T]: ...
    async def delete(self, entity: T) -> None: ...
    async def commit(self) -> None: ...
    async def close(self) -> None: ...
```

### 2) Infrastructure: DB 연동 및 ORM 모델 구현

- `infrastructure/db/base.py`에서 비동기 SQLAlchemy 엔진과 세션 팩토리를 생성합니다.
- `infrastructure/db/models.py`에 `UserORM → SessionORM → ChatMessageORM` 관계를 정의합니다.
- `cascade="all, delete-orphan"`과 `ondelete="CASCADE"`를 설정해 세션 삭제 시 메시지가 함께 삭제됩니다.
- `infrastructure/mydb_repository.py`에서 `MyDBPort[T]`를 구현하는 제네릭 레포지토리를 만듭니다.

```py
# infrastructure/db/models.py
class SessionORM(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    messages = relationship("ChatMessageORM", back_populates="session",
                            lazy="selectin", cascade="all, delete-orphan")

class ChatMessageORM(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

```py
# infrastructure/mydb_repository.py
class MyDBRepository(MyDBPort[T], Generic[T]):
    def __init__(self, entity_class: Type[T]):
        self.entity_class = entity_class
        engine = get_engine(os.getenv("DATABASE_URL"))
        session_factory = get_session_factory(engine)
        self.session: AsyncSession = session_factory()

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def filter_by(self, **kwargs) -> List[T]:
        result = await self.session.execute(
            select(self.entity_class).filter_by(**kwargs)
        )
        return result.scalars().all()
```

### 3) Application: 유스케이스에서 세션과 메시지 흐름 관리

- `application/session_usecases.py`에서 세션 생성·삭제·조회를 담당합니다.
- `application/openai_usecases.py`의 `generate_stream_response`에서 스트리밍 전에 사용자 메시지를 저장하고, 스트리밍 완료 후 어시스턴트 전체 응답을 저장합니다.

```py
# application/session_usecases.py
class SessionUsecase:
    def __init__(self):
        self.session_repository = MyDBRepository(entity_class=SessionORM)
        self.chat_repository = MyDBRepository(entity_class=ChatMessageORM)
        self.user_repository = MyDBRepository(entity_class=UserORM)

    async def create_session_id(self, ai_request: OpenAIResponseAPIModel) -> int:
        new_session = SessionORM(
            user_id=1,
            title=ai_request.input[:20] if isinstance(ai_request.input, str) else "New Session",
        )
        await self.session_repository.add(new_session)
        session_id = new_session.id
        await self.session_repository.commit()
        return session_id

    async def delete_session(self, session_id: int) -> str:
        session = await self.session_repository.get_by_id(session_id)
        await self.session_repository.delete(session)
        await self.session_repository.commit()
        return "세션 삭제 완료"
```

```py
# application/openai_usecases.py  (generate_stream_response 발췌)
async def generate_stream_response(self, ai_request, session_id: int):
    # 1. 스트리밍 전: 사용자 메시지 저장
    user_message_entity = ChatMessageORM(
        session_id=session_id, role="user", message=user_message
    )
    await self.chat_repository.add(user_message_entity)
    await self.chat_repository.commit()

    # 2. 스트리밍 응답 생성 + chunk 전달
    response = await self.openai_repository.create_response(**request_data)
    async for chunk in self.openai_repository.output_response_stream(response):
        chat.append(chunk)
        yield chunk

    # 3. 스트리밍 후: 어시스턴트 전체 응답 저장
    chat_message_entity = ChatMessageORM(
        role="assistant", message=''.join(chat), session_id=session_id
    )
    await self.chat_repository.add(chat_message_entity)
    await self.chat_repository.commit()
```

### 4) API: 세션 관리 엔드포인트 + SSE 세션 연동

- `api/session/router.py`에서 세션 CRUD 및 유저 관리 엔드포인트를 제공합니다.
- `api/openai_response/router.py`의 SSE 엔드포인트에서 `session_id`가 없으면 새 세션을 생성하고, 첫 번째 SSE 이벤트로 `session_id`를 내려줍니다.

```py
# api/session/router.py
@router.get("/sessions/{user_id}", response_model=ResponseAPI[List[Session]])
async def get_sessions(user_id: int):
    sessions = await session_usecase.get_sessions_by_user(user_id)
    sessions = [Session.model_validate(s, from_attributes=True) for s in sessions]
    return ResponseAPI(status_code=200, message="세션 목록 조회 성공", data=sessions)

@router.delete("/sessions/{session_id}", response_model=ResponseAPI)
async def delete_session(session_id: int):
    success_message = await session_usecase.delete_session(session_id)
    return ResponseAPI(status_code=200, message=success_message)
```

```py
# api/openai_response/router.py  (SSE 엔드포인트 발췌)
@router.post("/sse")
async def get_openai_response_sse(data: OpenAIResponseAPIModel):
    if data.session_id is None:
        session_id = await session_usecase.create_session_id(data)
    else:
        session_id = data.session_id

    async def event_generator():
        yield f"event: session\ndata: {session_id}\n\n"  # 세션 ID를 첫 이벤트로 전송
        async for chunk in openai_usecase.generate_stream_response(
            ai_request=data, session_id=session_id
        ):
            yield format_sse_data(chunk)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

</details>

## 개선 사항

> 아래 항목은 다음 단계에서 개선할 예정입니다.

- agents sdk를 도입해 에이전트간의 오케스트레이션 관리 기능 및 MCP 사용 기능 추가
