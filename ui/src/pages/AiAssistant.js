import '../App.css';
import "milligram";

const AiAssistant = () => {


    return (
        <div className="container_main">
            <form>
                <fieldset>
                    <label htmlFor="ageRangeField">Choose your AI agent</label>
                    <select id="ageRangeField">
                        <option value="AI agent 1">AI agent 1</option>
                        <option value="AI agent 2">AI agent 2</option>
                        <option value="AI agent 3">AI agent 3</option>
                        <option value="AI agent 4">AI agent 4</option>
                        <option value="AI agent 5">AI agent 5</option>
                    </select>
                    <label htmlFor="commentField">Please provide How we can help you</label>
                    <textarea placeholder="Please ask question here" id="commentField" ></textarea>
                    <div className="float-right">
                        <input type="checkbox" id="confirmField"/>
                        <label className="label-inline" htmlFor="confirmField">Send a copy to yourself</label>
                    </div>
                    <input className="button-primary" type="submit" value="Send"/>
                </fieldset>
            </form>

        </div>
    );
};

export default AiAssistant;