import { createBrowserRouter } from "react-router-dom";

import Layout from "./Layout";
import Home from "./pages/Home";
import AiAssistant from "./pages/AiAssistant";
import Dashboard from "./pages/Dashboard";
import Scenarios from "./pages/Scenarios";
import AgentsConfiguration from "./pages/dashboard/agentsConfiguration";
import AgentsOverview from "./pages/dashboard/agentsOverview";

const router = createBrowserRouter([
    {
        element: <Layout />,
        children: [
            {
                path: "/",
                element: <Home />
            },
            {
                path: "/aiassistant",
                element: <AiAssistant />
            },
            {
                path: "/dashboard",
                element: <Dashboard />
            },
            {
                path: "/scenarios",
                element: <Scenarios />
            },
            {
                path: "/agentsConfiguration",
                element: <AgentsConfiguration />
            },
            {
                path: "/agentsOverview",
                element: <AgentsOverview />
            }
        ]
    }
]);

export default router;
