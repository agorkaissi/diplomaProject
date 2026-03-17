import './App.css';
import {Routes, Route} from "react-router-dom";
import "milligram";
import Home from "./Home";
import Layout from "./Layout";

function App() {
    return (
        <Routes element={<Layout />}>
            <Route exact path="/" element={<Home />} />
        </Routes>
    );
}

export default App;
