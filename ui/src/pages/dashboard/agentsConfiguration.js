import '../../App.css';
import "milligram";
import {Link} from "react-router-dom";

const AgentsConfiguration = () => {


    return (
      <div className="container_main">
            <div className="dashboard_view">
            <div><Link to="/dashboard" className="back-button">
                ← Back to Dashboard
            </Link></div>

            </div>
      </div>
    );
};

export default AgentsConfiguration;