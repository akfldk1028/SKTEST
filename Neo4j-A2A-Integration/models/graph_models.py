"""
Neo4j Graph Data Models for A2A Integration
Defines the structure of nodes and relationships in our graph
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from uuid import uuid4

class BaseNode(BaseModel):
    """Base class for all graph nodes"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for Neo4j"""
        return self.dict()

class UserNode(BaseNode):
    """Represents a user/human participant in conversations"""
    label: str = "User"
    session_id: str
    user_type: str = "human"  # human, system, test
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Analytics fields
    total_conversations: int = 0
    total_messages: int = 0
    last_active: Optional[datetime] = None

class AgentNode(BaseNode):
    """Represents an AI agent in the A2A network"""
    label: str = "Agent"
    name: str
    agent_type: str  # travel_agent, flight_agent, hotel_agent, etc.
    endpoint: str  # A2A endpoint URL
    description: Optional[str] = None
    version: str = "1.0.0"
    
    # Agent capabilities
    skills: List[str] = Field(default_factory=list)
    supported_operations: List[str] = Field(default_factory=list)
    
    # Performance metrics
    total_requests: int = 0
    total_responses: int = 0
    success_rate: float = 0.0
    average_response_time: float = 0.0
    
    # Status
    is_active: bool = True
    last_health_check: Optional[datetime] = None

class ConversationNode(BaseNode):
    """Represents a complete conversation session"""
    label: str = "Conversation"
    conversation_id: str
    context_id: str  # Links to external conversation context
    status: str = "active"  # active, completed, failed, abandoned
    
    # Conversation metadata
    topic: Optional[str] = None
    intent: Optional[str] = None  # flight_booking, hotel_search, etc.
    language: str = "en"
    
    # Metrics
    message_count: int = 0
    agent_count: int = 0  # Number of different agents involved
    duration_seconds: Optional[float] = None
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    
    # Success metrics
    was_successful: Optional[bool] = None
    user_satisfaction: Optional[int] = None  # 1-5 rating

class MessageNode(BaseNode):
    """Represents individual messages in conversations"""
    label: str = "Message"
    message_id: str
    conversation_id: str
    
    # Message content
    content: str
    role: str  # user, agent, system
    message_type: str = "text"  # text, image, file, structured_data
    
    # A2A specific fields
    a2a_request_id: Optional[str] = None
    a2a_response_id: Optional[str] = None
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.now)
    response_time_ms: Optional[float] = None
    
    # Processing info
    tokens_used: Optional[int] = None
    processing_cost: Optional[float] = None
    
    # Status
    status: str = "sent"  # sent, delivered, read, failed
    error_message: Optional[str] = None

class SkillNode(BaseNode):
    """Represents agent skills/capabilities"""
    label: str = "Skill"
    skill_id: str
    name: str
    description: str
    category: str  # booking, search, analysis, etc.
    
    # Usage metrics
    usage_count: int = 0
    success_rate: float = 0.0

class IntentNode(BaseNode):
    """Represents user intents/goals"""
    label: str = "Intent"
    intent_id: str
    name: str
    description: str
    category: str
    
    # Success patterns
    common_patterns: List[str] = Field(default_factory=list)
    success_indicators: List[str] = Field(default_factory=list)

# Relationship Types
class RelationshipType:
    """Defines the types of relationships in our graph"""
    
    # User relationships
    STARTS_CONVERSATION = "STARTS_CONVERSATION"
    SENDS_MESSAGE = "SENDS_MESSAGE"
    HAS_INTENT = "HAS_INTENT"
    
    # Agent relationships
    RESPONDS_TO = "RESPONDS_TO"
    DELEGATES_TO = "DELEGATES_TO"
    COLLABORATES_WITH = "COLLABORATES_WITH"
    HAS_SKILL = "HAS_SKILL"
    HANDLES_INTENT = "HANDLES_INTENT"
    
    # Conversation relationships
    CONTAINS_MESSAGE = "CONTAINS_MESSAGE"
    INVOLVES_AGENT = "INVOLVES_AGENT"
    FOLLOWS_CONVERSATION = "FOLLOWS_CONVERSATION"  # For conversation chains
    
    # Message relationships
    REPLIES_TO = "REPLIES_TO"
    TRIGGERS_ACTION = "TRIGGERS_ACTION"
    
    # Temporal relationships
    HAPPENS_BEFORE = "HAPPENS_BEFORE"
    HAPPENS_AFTER = "HAPPENS_AFTER"

class Relationship(BaseModel):
    """Base relationship model"""
    from_node: str  # Node ID
    to_node: str    # Node ID
    rel_type: str   # Relationship type
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    
    def to_cypher_create(self) -> str:
        """Generate Cypher CREATE statement for this relationship"""
        props = ", ".join([f"{k}: ${k}" for k in self.properties.keys()])
        if props:
            props = "{" + props + ", created_at: datetime()}"
        else:
            props = "{created_at: datetime()}"
            
        return f"MATCH (a {{id: $from_node}}), (b {{id: $to_node}}) CREATE (a)-[r:{self.rel_type} {props}]->(b)"

# Graph Schema Utilities
class GraphSchema:
    """Utility class for graph schema operations"""
    
    @staticmethod
    def get_node_constraints() -> List[str]:
        """Get list of Neo4j constraints to create"""
        return [
            "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.id IS UNIQUE",
            "CREATE CONSTRAINT agent_id_unique IF NOT EXISTS FOR (a:Agent) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT conversation_id_unique IF NOT EXISTS FOR (c:Conversation) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT message_id_unique IF NOT EXISTS FOR (m:Message) REQUIRE m.id IS UNIQUE",
            "CREATE CONSTRAINT skill_id_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT intent_id_unique IF NOT EXISTS FOR (i:Intent) REQUIRE i.id IS UNIQUE",
        ]
    
    @staticmethod
    def get_node_indexes() -> List[str]:
        """Get list of Neo4j indexes to create"""
        return [
            "CREATE INDEX user_session_idx IF NOT EXISTS FOR (u:User) ON (u.session_id)",
            "CREATE INDEX agent_name_idx IF NOT EXISTS FOR (a:Agent) ON (a.name)",
            "CREATE INDEX agent_type_idx IF NOT EXISTS FOR (a:Agent) ON (a.agent_type)",
            "CREATE INDEX conversation_context_idx IF NOT EXISTS FOR (c:Conversation) ON (c.context_id)",
            "CREATE INDEX conversation_intent_idx IF NOT EXISTS FOR (c:Conversation) ON (c.intent)",
            "CREATE INDEX message_timestamp_idx IF NOT EXISTS FOR (m:Message) ON (m.timestamp)",
            "CREATE INDEX message_conversation_idx IF NOT EXISTS FOR (m:Message) ON (m.conversation_id)",
            "CREATE INDEX skill_category_idx IF NOT EXISTS FOR (s:Skill) ON (s.category)",
            "CREATE INDEX intent_category_idx IF NOT EXISTS FOR (i:Intent) ON (i.category)",
        ]
    
    @staticmethod
    def create_sample_data() -> List[str]:
        """Generate sample data for testing"""
        return [
            # Sample Users
            """CREATE (u1:User {
                id: 'user_1',
                session_id: 'session_001',
                user_type: 'human',
                name: 'John Doe',
                created_at: datetime(),
                total_conversations: 5,
                total_messages: 25
            })""",
            
            # Sample Agents
            """CREATE (a1:Agent {
                id: 'travel_agent_1',
                name: 'TravelPlanningAgent',
                agent_type: 'travel_agent',
                endpoint: 'http://localhost:8000',
                description: 'Main travel planning and coordination agent',
                version: '1.0.0',
                skills: ['trip_planning', 'coordination', 'customer_service'],
                is_active: true,
                created_at: datetime(),
                total_requests: 15,
                total_responses: 15,
                success_rate: 0.95,
                average_response_time: 1.5
            })""",
            
            """CREATE (a2:Agent {
                id: 'flight_agent_1',
                name: 'FlightBookingAgent',
                agent_type: 'flight_agent',
                endpoint: 'http://localhost:9999',
                description: 'Specialized flight search and booking agent',
                version: '1.0.0',
                skills: ['flight_search', 'booking', 'pricing'],
                is_active: true,
                created_at: datetime(),
                total_requests: 10,
                total_responses: 9,
                success_rate: 0.90,
                average_response_time: 2.3
            })""",
            
            # Sample Skills
            """CREATE (s1:Skill {
                id: 'flight_booking_skill',
                skill_id: 'flight_booking',
                name: 'Flight Booking',
                description: 'Search and book flights',
                category: 'booking',
                usage_count: 50,
                success_rate: 0.92,
                created_at: datetime()
            })""",
            
            # Sample Intents
            """CREATE (i1:Intent {
                id: 'book_flight_intent',
                intent_id: 'book_flight',
                name: 'Book Flight',
                description: 'User wants to book a flight',
                category: 'booking',
                common_patterns: ['book flight', 'need flight', 'fly to'],
                created_at: datetime()
            })""",
            
            # Relationships
            "MATCH (a:Agent {id: 'travel_agent_1'}), (s:Skill {id: 'flight_booking_skill'}) CREATE (a)-[:HAS_SKILL]->(s)",
            "MATCH (a:Agent {id: 'flight_agent_1'}), (s:Skill {id: 'flight_booking_skill'}) CREATE (a)-[:HAS_SKILL]->(s)",
            "MATCH (a:Agent {id: 'flight_agent_1'}), (i:Intent {id: 'book_flight_intent'}) CREATE (a)-[:HANDLES_INTENT]->(i)",
        ]