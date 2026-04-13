import '../App.css';
import "milligram";
import { useNavigate } from "react-router-dom";

const Dashboard = () => {
    const navigate = useNavigate();

    return (
        <div className="container_main">
            <div className="dashboard">
                <div className="tile" onClick={() => navigate("/agentsOverview")}>
                    <h5>Agents</h5>
                    <h5>Overview</h5>
                </div>

                <div className="tile" onClick={() => navigate("/agentsConfiguration")}>
                    <h5>Agents</h5>
                    <h5>Configuration</h5>
                </div>

                <div className="tile">
                    <h5>Chat</h5>
                    <h5>Logs</h5>
                </div>

                <div className="tile">Monitoring</div>
                <div className="tile">Performance</div>
                <div className="tile">FunctionA</div>

                <div className="tile">FunctionB</div>
                <div className="tile">FunctionC</div>
                <div className="tile">FunctionD</div>
            </div>
        </div>
    );
};

export default Dashboard;