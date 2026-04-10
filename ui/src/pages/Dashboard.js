import '../App.css';
import "milligram";

const Dashboard = () => {


    return (
        <div className="container_main">
            <div className="dashboard_view">
                To do - implement on dashboard MVP: <br />
                1. Agents overview: <br />
                    - list of agents <br />
                    - status of agents <br />
                    - activity <br />
                    - numbers of questions asked? <br />
                2. Agent configuration:<br />
                    - add <br />
                    - remove (put on hold) <br />
                    - edit? <br />
                3. Chat logs: <br />
                    - history of chats with agents <br />
                4. Monitoring & observability: <br />
                    - numer of asks per agent<br />
                    - time of response<br />
                    - CPU/GPU
                    - response time
            </div>
        </div>
    );
};

export default Dashboard;