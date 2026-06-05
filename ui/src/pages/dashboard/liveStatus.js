import '../../App.css';
import "milligram";
import {useEffect, useState} from "react";
import {Link} from "react-router-dom";

const LiveStatus = () => {
    const [status, setStatus] = useState("checking");
    const [latency, setLatency] = useState(null);
    const [lastCheck, setLastCheck] = useState(null);

    const [agents, setAgents] = useState([]);
    const [loading, setLoading] = useState(true);

    const [folders, setFolders] = useState([]);
    const [documents, setDocuments] = useState([]);
    const [loading2, setLoading2] = useState(true);



    const checkBackend = async () => {
        const start = Date.now();

        try {
            const response = await fetch(
                "http://localhost:8000/healthcheck"
            );

            const end = Date.now();

            if (!response.ok) {
                throw new Error();
            }

            const data = await response.json();

            if (data.status === "ok") {
                setStatus("online");
                setLatency(end - start);
            } else {
                setStatus("offline");
            }
        } catch {
            setStatus("offline");
            setLatency(null);
        }

        setLastCheck(
            new Date().toLocaleTimeString()
        );
    };

    useEffect(() => {
        checkBackend();

        const interval = setInterval(
            checkBackend,
            10000
        );

        return () => clearInterval(interval);
    }, []);


    const fetchAgents = async () => {
        try {
            const res = await fetch("http://localhost:8000/agents");
            const data = await res.json();

            setAgents(data);
        } catch (e) {
            setAgents([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAgents();

        const interval = setInterval(fetchAgents, 10000);
        return () => clearInterval(interval);
    }, []);

    const total = agents.length;

    const active = agents.filter(a => a.active).length;

    const supervisors = agents.filter(
        a => a.agent_type === "supervisor"
    ).length;

    const specialists = agents.filter(
        a => a.agent_type === "specialist"
    ).length;

    const totalConnections = agents.reduce(
        (sum, a) => sum + (a.connected_agent_ids?.length || 0),
        0
    );


    const fetchDocuments = async () => {
        try {
            const res = await fetch("http://localhost:8000/documents");
            const data = await res.json();

            setFolders(data.folders);

            const allDocs = [];

            for (const folder of data.folders) {
                const resDocs = await fetch(
                    `http://localhost:8000/documents/${folder.name}`
                );

                const folderData = await resDocs.json();

                folderData.documents.forEach(doc => {
                    allDocs.push({
                        ...doc,
                        folder: folder.name,
                    });
                });
            }

            allDocs.sort(
                (a, b) =>
                    new Date(b.modified_at) -
                    new Date(a.modified_at)
            );

            setDocuments(allDocs);

        } catch (e) {
            setFolders([]);
            setDocuments([]);
        } finally {
            setLoading2(false);
        }
    };

    useEffect(() => {
        fetchDocuments();

        const interval = setInterval(fetchDocuments, 10000);
        return () => clearInterval(interval);
    }, []);


    const totalFolders = folders.length;
    const totalFiles = documents.length;

    const latestDocument = documents[0];



    return (
        <div className="container_main">
            <div className="dashboard_view_2">
                <div className="back-container">
                    <Link to="/dashboard" className="back-button">
                        ← Back to Dashboard
                    </Link>
                </div>
                <div className="container_live">
                    <div className="status-card">
                        <h3>
                            Backend Status
                        </h3>

                        <div className="status-row">
                          <span
                              className={`status-dot ${status}`}
                          ></span>

                            <strong>
                                {status === "online" &&
                                    "ONLINE"}

                                {status === "offline" &&
                                    "OFFLINE"}

                                {status === "checking" &&
                                    "CHECKING"}
                            </strong>
                        </div>

                        <p>
                            <strong>Ping:</strong>{" "}
                            {latency
                                ? `${latency} ms`
                                : "--"}
                        </p>

                        <p>
                            <strong>Last check:</strong>{" "}
                            {lastCheck || "--"}
                        </p>
                    </div>


                    <div className="status-card">
                        <h3>Agents</h3>

                        {loading ? (
                            <p>Loading...</p>
                        ) : (
                            <>
                                <p><strong>Total:</strong> {total}</p>
                                <p><strong>Active:</strong> {active}</p>
                                <p><strong>Total connections:</strong> {totalConnections}</p>
                                <p><strong>Specialist:</strong> {specialists}</p>
                                <p><strong>Supervisor:</strong> {supervisors}</p>

                            </>
                        )}
                    </div>

                    <div className="status-card">
                        <h3>Documents Status</h3>

                        {loading2 ? (
                            <p>Loading...</p>
                        ) : (
                            <>
                                <p><strong>Folders:</strong> {totalFolders}</p>
                                <p><strong>Files:</strong> {totalFiles}</p>

                                <p>
                                    <strong>Latest:</strong>{" "}
                                    {latestDocument
                                        ? `${latestDocument.filename} (${latestDocument.folder})`
                                        : "—"}
                                </p>
                            </>
                        )}
                    </div>

                </div>

            </div>
        </div>
    );
};

export default LiveStatus;