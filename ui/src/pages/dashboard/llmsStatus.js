import '../../App.css';
import "milligram";
import {Link} from "react-router-dom";
import {useEffect, useState} from "react";

const LlmsStatus = () => {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchModels = async () => {
        try {
            const res = await fetch("http://localhost:8000/llm/status");
            const data = await res.json();
            setModels(data.models || []);
        } catch (err) {
            console.error("Failed to fetch LLM status:", err);
            setModels([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchModels();
        const interval = setInterval(fetchModels, 60000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="container_main">
            <div className="dashboard_view_2">
                <div className="back-container">
                    <Link to="/dashboard" className="back-button">
                        ← Back to Dashboard
                    </Link>
                </div>

                <div className="container_live">
                    {loading ? (
                        <p>Loading...</p>
                    ) : models.length === 0 ? (
                        <p>No models available</p>
                    ) : (
                        models.map((model) => (
                            <div className="status-card" key={model.name}>
                                <h3>{model.name}</h3>
                                <div className="status-row">
                  <span
                      className={`status-dot ${
                          model.status === "online"
                              ? "online"
                              : model.status === "offline"
                                  ? "offline"
                                  : "checking"
                      }`}
                  ></span>
                                    <strong>{model.status.toUpperCase()}</strong>
                                </div>
                                <p><strong>Version:</strong> {model.version}</p>
                                <p><strong>Loaded:</strong> {model.loaded ? "Yes" : "No"}</p>
                                <p><strong>Context length:</strong> {model.context_length}</p>
                                <p><strong>Memory usage:</strong> {model.memory_usage}</p>
                                <p><strong>Uptime:</strong> {model.uptime}</p>
                            </div>
                        ))
                    )}
                </div>
            </div>
        </div>
    );
};


export default LlmsStatus;