# Neo4j + A2A Integration: Graph Relationships Documentation

## 개요
Neo4j 그래프 데이터베이스와 A2A (Agent-to-Agent) 프로토콜을 통합한 시스템에서 생성되는 노드와 관계들을 문서화합니다.

## 노드 구조 (Nodes)

### 1. User 노드
```cypher
(:User {
  id: "uuid",
  session_id: "string",
  user_type: "human",
  name: "string",
  created_at: datetime,
  total_conversations: integer,
  total_messages: integer
})
```

### 2. Agent 노드
```cypher
(:Agent {
  id: "uuid",
  name: "TravelPlanningAgent | FlightBookingAgent",
  agent_type: "travel_agent | flight_agent",
  endpoint: "http://localhost:port",
  created_at: datetime,
  total_requests: integer,
  total_responses: integer,
  success_rate: float,
  is_active: boolean
})
```

### 3. Conversation 노드
```cypher
(:Conversation {
  id: "uuid",
  conversation_id: "string",
  context_id: "string",
  status: "active | completed",
  intent: "flight_booking | general_inquiry",
  started_at: datetime,
  ended_at: datetime,
  message_count: integer
})
```

### 4. Message 노드
```cypher
(:Message {
  id: "uuid",
  message_id: "string",
  conversation_id: "string",
  content: "string",
  role: "user | agent",
  message_type: "text | a2a_request | a2a_response",
  a2a_request_id: "string",
  a2a_response_id: "string",
  response_time_ms: float,
  timestamp: datetime,
  status: "sent"
})
```

## 관계 구조 (Relationships)

### 1. STARTS_CONVERSATION
**사용자가 대화를 시작**
```cypher
(User)-[:STARTS_CONVERSATION {timestamp: datetime}]->(Conversation)
```
- **목적**: 사용자와 대화 세션 연결
- **속성**: timestamp
- **개수**: 현재 2개

### 2. CONTAINS_MESSAGE
**대화가 메시지를 포함**
```cypher
(Conversation)-[:CONTAINS_MESSAGE]->(Message)
```
- **목적**: 대화와 해당 메시지들 연결
- **속성**: 없음
- **개수**: 현재 2개

### 3. SENDS_MESSAGE
**사용자/에이전트가 메시지를 전송**
```cypher
(User|Agent)-[:SENDS_MESSAGE]->(Message)
```
- **목적**: 메시지 발신자 식별
- **속성**: 없음
- **개수**: 현재 2개

### 4. DELEGATES_TO ⭐
**A2A 에이전트 간 통신 핵심 관계**
```cypher
(Agent)-[:DELEGATES_TO {timestamp: datetime, message_id: string}]->(Agent)
```
- **목적**: A2A 프로토콜을 통한 에이전트 간 업무 위임
- **속성**: timestamp, message_id
- **방향**: 양방향 (요청/응답)
- **개수**: 현재 2개

## 실제 A2A 통신 플로우

### 전체 관계 흐름 (ASCII 다이어그램)
```
┌─────────────────────────────────────────────────────────────────────┐
│                    Neo4j + A2A Graph Structure                     │
└─────────────────────────────────────────────────────────────────────┘

     [User]                    [Agent: TravelPlanning]
        │                              │
        │ STARTS_CONVERSATION          │ DELEGATES_TO
        ▼                              ▼
  [Conversation] ────CONTAINS_MESSAGE──► [Message]
        │                              ▲
        │                              │ SENDS_MESSAGE
        │                              │
        └────CONTAINS_MESSAGE──► [Message] ◄─── SENDS_MESSAGE
                                      ▲
                                      │
                               [Agent: FlightBooking]

┌─────────────────────────────────────────────────────────────────────┐
│                      상세 A2A 통신 플로우                            │
└─────────────────────────────────────────────────────────────────────┘

(1) 사용자 요청:  "I want to go to Seoul"
    │
    ▼
(2) [User] ──STARTS_CONVERSATION──► [Conversation]
    │
    ▼
(3) [User] ──SENDS_MESSAGE──► [Message: "Seoul request"]
    │
    ▼
(4) [TravelPlanningAgent] ──DELEGATES_TO──► [FlightBookingAgent]
    │                                            │
    │                                            │ (A2A 프로토콜)
    │                                            ▼
(5) [FlightBookingAgent] ──SENDS_MESSAGE──► [Message: A2A_REQUEST]
    │
    ▼
(6) [FlightBookingAgent] ──DELEGATES_TO──► [TravelPlanningAgent]
    │                                            │
    │                                            ▼
(7) [TravelPlanningAgent] ──SENDS_MESSAGE──► [Message: A2A_RESPONSE]
    │
    ▼
(8) 사용자에게 최종 응답 전달

┌─────────────────────────────────────────────────────────────────────┐
│                      노드별 관계 맵 (ASCII)                          │
└─────────────────────────────────────────────────────────────────────┘

                    ┌─────────────┐
                    │    User     │
                    │  (2 nodes)  │
                    └──────┬──────┘
                           │ STARTS_CONVERSATION (2)
                           ▼
                  ┌─────────────────┐
                  │  Conversation   │
                  │   (2 nodes)     │
                  └────────┬────────┘
                           │ CONTAINS_MESSAGE (2)
                           ▼
   ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
   │ TravelPlanning  │ │    Message      │ │ FlightBooking   │
   │     Agent       │─┤   (5 nodes)    │◄┤     Agent       │
   │   (1 node)      │ └─────────────────┘ │   (1 node)      │
   └─────────┬───────┘                     └─────────┬───────┘
             │                                       │
             └───────── DELEGATES_TO (2) ────────────┘
             ◄─────────────────────────────────────────

┌─────────────────────────────────────────────────────────────────────┐
│                    메시지 플로우 다이어그램                           │
└─────────────────────────────────────────────────────────────────────┘

Time ──────────────────────────────────────────────────────────────►

User Input:
│ "I want to go to Seoul"
│
├─► User ──SENDS_MESSAGE──► Message(1) ──┐
│                                        │
│                                        ▼
├─► TravelAgent ──DELEGATES_TO──► FlightAgent
│                                        │
│                                        ▼
├─► FlightAgent ──SENDS_MESSAGE──► Message(2): A2A_REQUEST
│                                        │
│                                        ▼
├─► FlightAgent ──DELEGATES_TO──► TravelAgent  
│                                        │
│                                        ▼
└─► TravelAgent ──SENDS_MESSAGE──► Message(3): A2A_RESPONSE
                                         │
                                         ▼
                                   User Response:
                                   "Flight options found..."
```

### A2A 상세 플로우
1. **사용자 요청**: "I want to go to Seoul"
2. **대화 시작**: User --[STARTS_CONVERSATION]--> Conversation
3. **사용자 메시지**: User --[SENDS_MESSAGE]--> Message
4. **에이전트 위임**: TravelPlanningAgent --[DELEGATES_TO]--> FlightBookingAgent
5. **A2A 응답**: FlightBookingAgent --[DELEGATES_TO]--> TravelPlanningAgent
6. **최종 응답**: TravelPlanningAgent --[SENDS_MESSAGE]--> Message

## 현재 데이터베이스 상태

### 노드 개수
- **Message**: 5개
- **User**: 2개
- **Conversation**: 2개
- **Agent**: 2개
- **TestNode**: 1개

### 관계 개수
- **STARTS_CONVERSATION**: 2개
- **CONTAINS_MESSAGE**: 2개
- **SENDS_MESSAGE**: 2개
- **DELEGATES_TO**: 2개 ⭐

## Neo4j 쿼리 예제

### 전체 그래프 시각화
```cypher
MATCH (n)-[r]->(m) RETURN n,r,m LIMIT 50
```

### A2A 에이전트 통신 추적
```cypher
MATCH (a1:Agent)-[r:DELEGATES_TO]->(a2:Agent)
RETURN a1.name, a2.name, r.timestamp, r.message_id
```

### 대화별 메시지 흐름
```cypher
MATCH (u:User)-[:STARTS_CONVERSATION]->(c:Conversation)-[:CONTAINS_MESSAGE]->(m:Message)
RETURN u.name, c.context_id, m.content, m.timestamp
ORDER BY m.timestamp
```

### 에이전트 성능 분석
```cypher
MATCH (a:Agent)
RETURN a.name, a.total_requests, a.total_responses, a.success_rate
ORDER BY a.total_requests DESC
```

## 고급 분석 쿼리

### 에이전트 간 협업 패턴
```cypher
MATCH (a1:Agent)-[:DELEGATES_TO]->(a2:Agent)-[:DELEGATES_TO]->(a1)
RETURN a1.name as agent1, a2.name as agent2, count(*) as collaboration_count
```

### 대화 성공률 분석
```cypher
MATCH (c:Conversation)
WHERE c.was_successful IS NOT NULL
RETURN c.intent, 
       count(*) as total_conversations,
       sum(case when c.was_successful then 1 else 0 end) as successful,
       round(100.0 * sum(case when c.was_successful then 1 else 0 end) / count(*), 2) as success_rate
```

### 응답 시간 분석
```cypher
MATCH (m:Message)
WHERE m.response_time_ms IS NOT NULL
RETURN m.message_type,
       avg(m.response_time_ms) as avg_response_time,
       min(m.response_time_ms) as min_response_time,
       max(m.response_time_ms) as max_response_time
```

## 시스템 아키텍처

### 기술 스택
- **그래프 DB**: Neo4j 5.x
- **A2A 프로토콜**: JSON-RPC over HTTP
- **AI 프레임워크**: Semantic Kernel
- **웹 프레임워크**: FastAPI
- **LLM**: OpenAI GPT-3.5-turbo

### 포트 구성
- **Neo4j Enhanced Server**: 8001
- **Flight Booking Agent**: 9999
- **Travel Agent**: 8000
- **Neo4j Browser**: 7474
- **Neo4j Database**: 7687

## 시스템 토폴로지 (ASCII)
  MATCH (n)-[r]->(m)
  RETURN n, r, m
  LIMIT 25


```
┌───────────────────────────────────────────────────────────────────────────┐
│                          Neo4j + A2A System Topology                     │
└───────────────────────────────────────────────────────────────────────────┘

 Web Browser              FastAPI Server           Neo4j Database
┌─────────────┐         ┌─────────────────────┐    ┌─────────────────┐
│             │  HTTP   │                     │    │                 │
│ User Input  │◄──────► │ Enhanced Travel     │◄──►│ Graph Database  │
│ :8001       │         │ Agent :8001         │    │ :7687          │
└─────────────┘         └──────────┬──────────┘    └─────────────────┘
                                   │                        ▲
                                   │ A2A Protocol           │
                                   │ (JSON-RPC)             │ Graph
                                   ▼                        │ Queries
                        ┌─────────────────────┐             │
                        │                     │             │
                        │ Flight Booking      │─────────────┘
                        │ Agent :9999         │
                        └─────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                        Data Flow Architecture                             │
└───────────────────────────────────────────────────────────────────────────┘

Step 1: User Request
   Browser ──HTTP POST──► FastAPI(:8001) ──► Neo4j Graph
                              │                    │
Step 2: Agent Processing      │                    ▼ 
   TravelAgent ──A2A──► FlightAgent(:9999)    [User]──►[Conv]──►[Msg]
                              │                    │
Step 3: Response Chain        │                    ▼
   TravelAgent ◄─A2A─── FlightAgent          [Agent]──DELEGATES_TO──►[Agent]
        │                     │                    │
Step 4: Graph Storage         │                    ▼
   Neo4j Graph ◄──────────────┘              All relationships stored
        │
Step 5: Final Response
   Browser ◄──HTTP─── FastAPI

┌───────────────────────────────────────────────────────────────────────────┐
│                    Database Entity Relationship                           │
└───────────────────────────────────────────────────────────────────────────┘

        ╔═══════════════╗                    ╔════════════════╗
        ║     USER      ║────────────────────║   CONVERSATION ║
        ║               ║ STARTS_CONVERSATION ║                ║
        ║ - session_id  ║                    ║ - context_id   ║
        ║ - name        ║                    ║ - intent       ║
        ╚═══════════════╝                    ╚════════════════╝
                                                       │
                                            CONTAINS_MESSAGE
                                                       │
                                                       ▼
╔════════════════╗                         ╔════════════════╗
║     AGENT      ║─────── DELEGATES_TO ────║    MESSAGE     ║
║                ║         (A2A Core)      ║                ║
║ - name         ║                         ║ - content      ║
║ - agent_type   ║◄─── SENDS_MESSAGE ──────║ - role         ║
║ - endpoint     ║                         ║ - a2a_req_id   ║
║ - success_rate ║                         ║ - response_ms  ║
╚════════════════╝                         ╚════════════════╝
        ▲│                                          ▲
        ││                                          │
        │└──────── DELEGATES_TO ────────────────────┘
        │          (Bidirectional)
        │
   ╔═══════════╗
   ║  METRICS  ║ 
   ║           ║
   ║ • Performance
   ║ • Success Rate  
   ║ • Response Time
   ╚═══════════╝
```

## 결론

이 Neo4j + A2A 통합 시스템은 다음을 제공합니다:

1. **완전한 대화 추적**: 사용자부터 에이전트까지 모든 상호작용 기록
2. **A2A 통신 시각화**: 에이전트 간 협업 패턴 분석 가능
3. **성능 모니터링**: 응답 시간, 성공률 등 실시간 메트릭
4. **관계형 분석**: 그래프 데이터베이스의 장점을 활용한 복잡한 쿼리
5. **확장성**: 새로운 에이전트와 관계 타입 쉽게 추가 가능

**현재 시스템은 완전히 작동하며, 모든 노드와 관계가 정상적으로 생성되고 있습니다.** 🚀