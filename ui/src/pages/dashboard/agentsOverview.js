import '../../App.css';
import "milligram";
import {useEffect, useState} from "react";
import {Link} from "react-router-dom";

const AgentsOverview = () => {
    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchAgents = async () => {
            try {
                const res = await fetch("/agents");
                if (!res.ok) throw new Error("API Error");

                const data = await res.json();
                setAgents(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchAgents();
    }, []);

    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error: {error}</p>;

    return (
        <div className="container_main">
            <div><Link to="/dashboard" className="back-button">
                ← Back to Dashboard
            </Link></div>
            <div className="dashboard_view">

                <table>
                    <thead>
                    <tr>
                        <th>Id</th>
                        <th>Name</th>
                        <th>Description</th>
                        <th>Docs path</th>
                        <th>Prompt</th>
                        <th>Type</th>
                        <th>Active</th>
                        <th>Connected Agents</th>
                    </tr>
                    </thead>
                    <tbody>
                    {agents.map((agent) => (
                        <tr key={agent.id}>
                            <td>{agent.id}</td>
                            <td>{agent.name}</td>
                            <td>{agent.description}</td>
                            <td>{agent.docs_path}</td>
                            <td>{agent.prompt}</td>
                            <td>{agent.agent_type}</td>
                            <td>{agent.active ? "Active" : "Inactive"}</td>
                            <td>{agent.connected_agent_ids?.join(", ")}</td>
                        </tr>
                    ))}
                    </tbody>


                </table>
            </div>
        </div>
    );
};

export default AgentsOverview;