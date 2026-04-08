import '../App.css';
import "milligram";

const Dashboard = () => {


    return (
        <div className="container_main">
            <div className="dashboard_view">
                <div className="box1">
                    <ul>
                        <li>Agents</li>
                        <li>Chats</li>
                        <li>Settings</li>
                        <li>Logs</li>
                    </ul>
                </div>
                <div className="box2">
                    Organization structure

                </div>
            </div>
        </div>
    );
};

export default Dashboard;