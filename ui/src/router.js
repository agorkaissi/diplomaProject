import { createBrowserRouter } from "react-router-dom";

import Layout from "./Layout";
import Home from "./pages/Home";
import AiAssistant from "./pages/AiAssistant";
import Dashboard from "./pages/Dashboard";
import Scenarios from "./pages/Scenarios";

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
