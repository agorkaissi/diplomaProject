from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from db import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=True, index=True)
    description = Column(Text, nullable=True)
    docs_path = Column(String(255), nullable=False)
    prompt = Column(Text, nullable=False)
    agent_type = Column(String(50), nullable=False, default="specialist")
    active = Column(Boolean, nullable=False, default=True)

    supervisor_links = relationship(
        "AgentLink",
        foreign_keys= "AgentLink.supervisor_agent_id",
        back_populates="supervisor",
        cascade="all, delete-orphan",
    )

    child_links = relationship(
        "AgentLink",
        foreign_keys= "AgentLink.child_agent_id",
        back_populates="child",
    )


class AgentLink(Base):
    __tablename__ = "agent_links"
    id = Column(Integer, primary_key=True, index=True)

    supervisor_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True,
    )

    child_agent_id = Column(
        Integer,
        ForeignKey("agents.id"),
        nullable=False,
        index=True,
    )

    active = Column(Boolean, nullable=False, default=True)
    sort_order = Column(Integer, nullable=False, default=1)

    supervisor = relationship(
        "Agent",
        foreign_keys=[supervisor_agent_id],
        back_populates="supervisor_links",
    )

    child = relationship(
        "Agent",
        foreign_keys=[child_agent_id],
        back_populates="child_links",
    )

