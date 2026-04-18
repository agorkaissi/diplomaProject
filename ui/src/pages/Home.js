import '../App.css';
import "milligram";

const Home = () => {


    return (
        <div className="container_main">
            <details>
                <summary>Thesis title</summary>
                <p>Intelligent Organization – A RAG-Enabled Multi-Agent System for Enterprise Simulation and Knowledge
                    Management</p>
            </details>

            <details>
                <summary>Problem statement</summary>
                <p>Modern enterprises operate in increasingly complex and dynamic environments, characterized by rapidly
                    evolving organizational structures, shifting business requirements, and continuously growing volumes
                    of internal knowledge. Organizations are typically composed of multiple departments, each with
                    distinct responsibilities, workflows, and domain-specific expertise. This decentralized nature makes
                    coordination, communication, and efficient knowledge sharing inherently challenging.

                    Traditional enterprise systems and centralized AI solutions often fail to address these challenges
                    effectively. They tend to be rigid, difficult to adapt to organizational changes, and do not
                    accurately reflect the distributed structure of real-world enterprises. As a result, they provide
                    limited support for dynamic workflows and lack the ability to deliver context-aware assistance
                    tailored to specific roles or departments.

                    Another critical issue is the management of sensitive organizational data. Enterprises rely on large
                    amounts of internal knowledge, including documents, procedures, and proprietary information, which
                    must remain secure and within organizational boundaries. The increasing adoption of AI systems
                    raises concerns about data privacy, particularly when external models or services are involved.
                    Ensuring controlled access to knowledge while maintaining data confidentiality is therefore a key
                    requirement.

                    Consequently, there is a need for a more flexible, modular, and secure approach to modeling and
                    supporting enterprise operations—one that can adapt to dynamic organizational structures, enable
                    effective collaboration, and ensure safe utilization of internal knowledge.</p>
            </details>

            <details>
                <summary>Proposed solution</summary>
                <p>To address the aforementioned challenges, this thesis proposes the design and implementation of a
                    RAG-enabled multi-agent system for enterprise simulation and knowledge management. The system models
                    an organization as a collection of autonomous, specialized AI agents, where each agent represents a
                    specific department, role, or function within the enterprise.

                    This multi-agent architecture enables modularity and scalability, allowing agents to be dynamically
                    created, configured, and removed according to changing organizational needs. Agents can interact
                    with one another, collaborate on tasks, and simulate real-world enterprise workflows, thereby
                    reflecting the decentralized and dynamic nature of modern organizations.

                    To ensure effective and secure knowledge utilization, the system integrates Retrieval-Augmented
                    Generation (RAG) mechanisms. Each agent can access relevant, organization-specific data through
                    controlled retrieval processes, enabling context-aware responses without exposing sensitive
                    information outside the system. This approach improves the accuracy and relevance of generated
                    outputs while maintaining strict data privacy.

                    Furthermore, the proposed platform provides a flexible environment for configuring agent behavior,
                    defining roles, and orchestrating interactions between agents. This allows users to simulate various
                    organizational scenarios, optimize workflows, and explore the potential of AI-driven enterprise
                    support systems.

                    By combining multi-agent architectures with RAG-based knowledge access, the proposed solution aims
                    to deliver a scalable, adaptive, and secure system that addresses the limitations of traditional
                    enterprise tools and demonstrates a novel approach to intelligent organizational modeling.</p>
            </details>

            <details>
                <summary>MVP</summary>
                <p>The MVP consists of five specialized AI agents representing key enterprise departments (Management,
                    HR, IT, Sales, and Knowledge Base). The system demonstrates inter-agent communication, task
                    delegation, and RAG-based knowledge retrieval from internal data sources. It provides a simple
                    interface for interacting with agents and simulating basic organizational workflows.</p>
            </details>

            <details>
                <summary>Technology stack</summary>
                <p>
                    <ul>
                        <li>Backend: FastAPI + Uvicorn</li>
                        <li>Frontend: React</li>
                        <li>Runtime: Node.js (frontend), Python 3.12 (backend)</li>
                        <li>AI / Agents: LangGraph + LangChain + Ollama (local LLM)</li>
                        <li>Database: SQLAlchemy (RDBMS)</li>
                        <li>Validation: Pydantic</li>
                        <li>Architecture: async, multi-agent system</li>
                    </ul>

                </p>
            </details>

        </div>
    );
};

export default Home;