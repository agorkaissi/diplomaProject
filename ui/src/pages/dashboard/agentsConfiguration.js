import '../../App.css';
import "milligram";
import {Link} from "react-router-dom";
import {useState, useEffect} from "react";

const AgentsConfiguration = () => {
    const [mode, setMode] = useState(null);
    const [agents, setAgents] = useState([]);
    const [selectedAgentId, setSelectedAgentId] = useState(null);
    const selectedAgent = agents.find(a => a.id === selectedAgentId);
    const [formData, setFormData] = useState({
        name: "",
        description: "",
        docs_path: "",
        prompt: "",
        agent_type: "specialist",
        active: true,
        connected_agent_ids: []
    });

    useEffect(() => {
        fetch("/agents")
            .then(res => res.json())
            .then(data => setAgents(data));
    }, []);

    const createAgent = async () => {
        try {
            const res = await fetch("/agents", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(formData),
            });

            if (!res.ok) {
                const error = await res.json();
                alert(JSON.stringify(error));
                return;
            }

            setFormData({
                name: "",
                description: "",
                docs_path: "",
                prompt: "",
                agent_type: "specialist",
                active: true,
                connected_agent_ids: []
            });

        } catch (err) {
            console.error(err);
            alert("Error creating agent");
        }
    };

    const toggleAgentActive = async () => {
        if (!selectedAgentId) return;

        const agent = agents.find(a => a.id === selectedAgentId);
        if (!agent) return;

        const endpoint = agent.active
            ? `/agents/${selectedAgentId}/deactivate`
            : `/agents/${selectedAgentId}/activate`;

        try {
            const res = await fetch(endpoint, {
                method: "PATCH",
            });

            if (!res.ok) {
                const error = await res.json();
                alert(error.detail || "Error");
                return;
            }

            setAgents(prev =>
                prev.map(a =>
                    a.id === selectedAgentId
                        ? {...a, active: !a.active}
                        : a
                )
            );

            setSelectedAgentId(null);
            setMode(null);

        } catch (err) {
            console.error(err);
            alert("Error updating agent status");
        }
    };

    return (
        <div className="container_main">
            <div className="dashboard_view_2">
                <div className="back-container">
                    <Link to="/dashboard" className="back-button">
                        ← Back to Dashboard
                    </Link>
                </div>

                <div className="button-group">
                    <button
                        className="button button-black button-outline"
                        onClick={() => setMode("create")}
                    >
                        Add
                    </button>
                    <button className="button button-black button-outline">Edit</button>
                    <button
                        className="button button-black button-outline"
                        onClick={() => setMode("deactivate")}
                    >
                        Toggle Status
                    </button>
                </div>

                {mode === "create" && (
                    <div className="inline-form">
                        <h4>Create Agent</h4>

                        <input
                            placeholder="Name"
                            value={formData.name}
                            onChange={(e) =>
                                setFormData({...formData, name: e.target.value})
                            }
                        />
                        <input
                            placeholder="Description"
                            value={formData.description}
                            onChange={(e) =>
                                setFormData({...formData, description: e.target.value})
                            }
                        />
                        <input
                            placeholder="Docs path"
                            value={formData.docs_path}
                            onChange={(e) =>
                                setFormData({...formData, docs_path: e.target.value})
                            }
                        />
                        <textarea
                            placeholder="Prompt"
                            value={formData.prompt}
                            onChange={(e) =>
                                setFormData({...formData, prompt: e.target.value})
                            }
                        />

                        <select
                            value={formData.agent_type}
                            onChange={(e) =>
                                setFormData({...formData, agent_type: e.target.value})
                            }
                        >
                            <option value="specialist">specialist</option>
                            <option value="supervisor">supervisor</option>
                        </select>
                        {formData.agent_type === "supervisor" && (
                            <select
                                multiple
                                value={formData.connected_agent_ids}
                                onChange={(e) => {
                                    const values = Array.from(
                                        e.target.selectedOptions,
                                        (option) => Number(option.value)
                                    );

                                    setFormData({
                                        ...formData,
                                        connected_agent_ids: values
                                    });
                                }}
                            >
                                {agents
                                    .filter(a => a.agent_type === "specialist")
                                    .map(agent => (
                                        <option key={agent.id} value={agent.id}>
                                            {agent.name}
                                        </option>
                                    ))}
                            </select>
                        )}
                        <label>
                            Status Active:
                            <input
                                type="checkbox"
                                checked={formData.active}
                                onChange={(e) =>
                                    setFormData({...formData, active: e.target.checked})
                                }
                            />
                        </label>

                        <div className="form-actions">
                            <button type="button" className="button button-black" onClick={createAgent}>
                                Save
                            </button>

                            <button
                                type="button"
                                className="button button-outline"
                                onClick={() => setMode(null)}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}

                {mode === "deactivate" && (
                    <div className="inline-form">
                        <h4>Change agent status</h4>

                        <select
                            value={selectedAgentId || ""}
                            onChange={(e) => setSelectedAgentId(Number(e.target.value))}
                        >
                            <option value="">Select agent</option>
                            {agents.map(agent => (
                                <option key={agent.id} value={agent.id}>
                                    {agent.name} ({agent.active ? "Active" : "Inactive"})
                                </option>
                            ))}
                        </select>

                        {selectedAgent && (
                            <p>
                                Current status:{" "}
                                <b>{selectedAgent.active ? "Active" : "Inactive"}</b>
                                <br/>
                                Action:{" "}
                                <b>{selectedAgent.active ? "Deactivate" : "Activate"}</b>
                            </p>
                        )}

                        <div className="form-actions">
                            <button
                                className="button button-black"
                                onClick={toggleAgentActive}
                                disabled={!selectedAgentId}
                            >
                                Change Status
                            </button>

                            <button
                                className="button button-outline"
                                onClick={() => {
                                    setMode(null);
                                    setSelectedAgentId(null);
                                }}
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                )}

            </div>
        </div>
    );
};

export default AgentsConfiguration;