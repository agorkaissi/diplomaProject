import { createBrowserRouter } from "react-router-dom";

import Layout from "./Layout";
import Home from "./Home";
import AiAssistant from "./AiAssistant";
import Dashboard from "./Dashboard";
import Scenarios from "./Scenarios";

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
            }
        ]
    }
]);

export default router;
