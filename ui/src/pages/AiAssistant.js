import '../App.css';
import "milligram";
import {useEffect, useState} from "react";

const AiAssistant = () => {
    const [agents, setAgents] = useState([]);
    const [selectedAgent, setSelectedAgent] = useState("");
    const [question, setQuestion] = useState("");
    const [response, setResponse] = useState(null);

    useEffect(() => {
        fetch("/agents")
            .then((res) => res.json())
            .then((data) => setAgents(data))
            .catch((err) => console.error("Error fetching agents:", err));
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        const res = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                question: question,
                selected_agent: selectedAgent,
            }),
        });

        const data = await res.json();
        setResponse(data);
    };


    return (
        <div className="container_main">
            <form onSubmit={handleSubmit}>
                <fieldset>
                    <label htmlFor="agentField">Choose your AI agent</label>
                    <select
                        id="agentField"
                        value={selectedAgent}
                        onChange={(e) => setSelectedAgent(e.target.value)}
                    >
                        <option value="">-- Select AI agent --</option>
                        {agents.map((agent) => (
                            <option key={agent.id} value={agent.name}>
                                {agent.name}
                            </option>
                        ))}
                    </select>
                    <label htmlFor="commentField">Please provide How we can help you</label>
                    <textarea
                        id="commentField"
                        placeholder="Please ask question here"
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                    />
                    <div className="float-right">
                        <input type="checkbox" id="confirmField"/>
                        <label className="label-inline" htmlFor="confirmField">Send a copy to yourself</label>
                    </div>
                    <input className="button-primary" type="submit" value="ASK"/>
                </fieldset>
                {response && (
                    <div>
                                <h4>Agent: {response.agent} Response</h4>
                                <p>{response.answer}</p>

                                <h4>Only for debug purpose (json):</h4>
                                <pre>{JSON.stringify(response, null, 2)}</pre>
                    </div>
                )}
            </form>

        </div>
    );
};

export default AiAssistant;