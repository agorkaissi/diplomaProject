import {NavLink, Outlet} from "react-router-dom";
import './App.css';

const Layout = () => {
    return (
        <>
            <header className="app-header">
                <div className="container header-row">
                    <h1 className="app-title">
                        <strong>ISSI diploma project </strong>
                    </h1>

                    <nav className="app-nav">
                        <NavLink to="/" end>Home</NavLink>
                        <NavLink to="/AiAssistant">AI Assistant</NavLink>
                        <NavLink to="/Dashboard">Dashboard</NavLink>
                        <NavLink to="/Scenarios">Scenarios</NavLink>
                    </nav>
                </div>
            </header>
            <main>
                <Outlet/>
            </main>
           <footer>
                <div className="container">
                    <strong>&#169; 2026 ISSI diploma project. All rights reserved</strong>
                    <div className="social-icons">

                        <a href="https://github.com/agorkaissi/diplomaProject" aria-label="GitHub" target="_blank" rel="noopener noreferrer">
                            <svg className="icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M12 .5C5.73.5.5 5.73.5 12c0 5.09 3.29 9.41 7.86 10.94.58.11.79-.25.79-.56v-2.02c-3.2.7-3.87-1.38-3.87-1.38-.53-1.34-1.29-1.7-1.29-1.7-1.05-.72.08-.7.08-.7 1.16.08 1.77 1.2 1.77 1.2 1.04 1.77 2.73 1.26 3.4.96.11-.75.41-1.26.74-1.55-2.55-.29-5.23-1.28-5.23-5.7 0-1.26.45-2.29 1.19-3.1-.12-.29-.52-1.47.11-3.07 0 0 .97-.31 3.18 1.18a11.1 11.1 0 0 1 5.8 0c2.21-1.49 3.18-1.18 3.18-1.18.63 1.6.23 2.78.11 3.07.74.81 1.19 1.84 1.19 3.1 0 4.43-2.69 5.41-5.25 5.69.42.36.79 1.07.79 2.16v3.2c0 .31.21.68.8.56A11.52 11.52 0 0 0 23.5 12C23.5 5.73 18.27.5 12 .5z"/>
                            </svg>
                        </a>
                    </div>
                </div>
            </footer>
        </>
    )
        ;
};

export default Layout;
