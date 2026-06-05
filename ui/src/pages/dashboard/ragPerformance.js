import '../../App.css';
import "milligram";
import {Link} from "react-router-dom";
import {useEffect, useState} from "react";

const RagPerformance = () => {

    const [metrics, setMetrics] = useState([]);

    const fetchMetrics = async () => {
        try {
            const res = await fetch("http://localhost:8000/metrics/rag");

            if (!res.ok) {
                throw new Error("Failed to fetch metrics");
            }

            const data = await res.json();
            setMetrics(data);

        } catch (err) {
            console.error("Metrics fetch error:", err);

        }
    };

    useEffect(() => {
        fetchMetrics();

        const interval = setInterval(fetchMetrics, 10000);

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
                    <div className="status-card">
                        <h3>RAG Performance</h3>

                        <>
                            <p>
                                <strong> AVG Retrieval time:</strong>{" "}
                                {metrics.avg_retrieval_time_ms?.toFixed(0)} ms
                            </p>

                            <p>
                                <strong> AVG Generation time:</strong>{" "}
                                {metrics.avg_generation_time_ms?.toFixed(0)} ms
                            </p>

                            <p>
                                <strong>AVG Total time:</strong>{" "}
                                {metrics.avg_total_time_ms?.toFixed(0)} ms
                            </p>

                            <p>
                                <strong>AVG Confidence:</strong>{" "}
                                {(metrics.avg_confidence * 100)?.toFixed(1)} %
                            </p>

                            <p>
                                <strong>Requests:</strong> {metrics.requests}
                            </p>
                        </>

                    </div>
                </div>
            </div>
        </div>
    );
};


export default RagPerformance;