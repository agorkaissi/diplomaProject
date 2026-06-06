import "../App.css";
import "milligram";
import { useState } from "react";

const scenarios = [
  {
    id: "hallucination",
    title: "Hallucination Resistance",
    question: "Who is Darth Vader in Harry Potter?",
    goal: "Verify whether the system invents information that is not present in indexed documents.",
    variants: [
      { name: "Llama OFF", model: "llama3.2:1b", reranker: "OFF", answer: "HarryPotter: Darth Vader.", result: "FAIL", score: 0, confidence: 0.2523, time: 4.18 },
      { name: "Gemma OFF", model: "gemma2:2b", reranker: "OFF", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 9.14 },
      { name: "Llama ON", model: "llama3.2:1b", reranker: "ON", answer: "Frodo: Darth Vader. HarryPotter: Darth Vader.", result: "FAIL", score: 0, confidence: 0.7224, time: 37.35 },
      { name: "Gemma ON", model: "gemma2:2b", reranker: "ON", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 61.44 },
    ],
    conclusion: "Gemma handled the hallucination scenario better. Llama generated unsupported answers even when reranker increased confidence.",
  },
  {
    id: "fallback",
    title: "Fallback",
    question: "How does a nuclear reactor work?",
    goal: "Check whether the system refuses to answer questions outside the indexed documents.",
    variants: [
      { name: "Llama OFF", model: "llama3.2:1b", reranker: "OFF", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 0.35 },
      { name: "Gemma OFF", model: "gemma2:2b", reranker: "OFF", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 0.03 },
      { name: "Llama ON", model: "llama3.2:1b", reranker: "ON", answer: "HarryPotter: Harry.", result: "FAIL", score: 0, confidence: 0.7198, time: 39.84 },
      { name: "Gemma ON", model: "gemma2:2b", reranker: "ON", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 70.5 },
    ],
    conclusion: "Reranker increased confidence for Llama, but also caused an incorrect accepted answer. This shows that confidence is not equal to correctness.",
  },
  {
    id: "comparison",
    title: "Comparison QA",
    question: "Compare Harry and Frodo",
    goal: "Evaluate whether the system can compare entities using only retrieved context.",
    variants: [
      { name: "Llama OFF", model: "llama3.2:1b", reranker: "OFF", answer: "Frodo: Frodo. HarryPotter: Harry Potter is the main character of the series.", result: "PARTIAL", score: 50, confidence: 0.367, time: 21.61 },
      { name: "Gemma OFF", model: "gemma2:2b", reranker: "OFF", answer: "I don't know based on the provided agent answers.", result: "PASS", score: 100, confidence: 0.0, time: 47.07 },
      { name: "Llama ON", model: "llama3.2:1b", reranker: "ON", answer: "HarryPotter: Harry, Ron, Hermione Granger. Frodo: Frodo.", result: "PARTIAL", score: 50, confidence: 0.7232, time: 38.7 },
      { name: "Gemma ON", model: "gemma2:2b", reranker: "ON", answer: "Frodo: Frodo, Harry", result: "FAIL", score: 0, confidence: 0.721, time: 66.27 },
    ],
    conclusion: "Comparison questions are difficult because retrieved chunks mention entities, but usually do not contain direct comparison facts.",
  },
];

const reportSections = [
  {
    title: "LLM model benchmark",
    content:
      "The benchmark compares llama3.2:1b and gemma2:2b in configurations with and without the Qwen reranker. Llama generates answers more aggressively, but it is more prone to unsupported answers. Gemma is more conservative and more likely to return a correct fallback when the context does not support the answer.",
  },
  {
    title: "Reranker impact",
    content:
      "The Qwen reranker increases confidence scores and improves the ranking of retrieved chunks. However, the experiments show that higher confidence does not automatically mean a correct final answer. In some cases, Llama with reranker achieved high confidence while still producing an unsupported answer.",
  },
  {
    title: "Hallucination analysis",
    content:
      "The hallucination tests show that Llama tends to copy entities from the user question, such as Darth Vader, even when those entities are not present in the retrieved context. Gemma performs better in this scenario because it more often returns the expected fallback answer.",
  },
  {
    title: "Retrieval error analysis",
    content:
      "Retrieval errors occur when the system retrieves chunks that contain similar entities, but not the actual information required to answer the question. This is especially visible in comparison questions, where the chunks mention Harry or Frodo but do not contain direct comparison facts.",
  },
  {
    title: "Generation error analysis",
    content:
      "Generation errors occur when the model receives context but produces an answer that is not supported by that context. The most common issues are entity copying, unsupported inference, over-answering and returning the wrong answer type, such as characters instead of objects or creatures.",
  },
  {
    title: "Supervisor evaluation",
    content:
      "The supervisor correctly calls child agents and aggregates their responses. However, it does not fully validate whether a child answer is supported by the retrieved context. As a result, it can accept an incorrect child answer if the response looks specific and confident.",
  },
  {
    title: "Prompt quality analysis",
    content:
      "The current prompt instructs the model to answer only from context and return fallback when the answer is unsupported. The results show that prompt rules alone are not enough for small local models. A programmatic validation layer is needed after generation.",
  },
  {
    title: "Failure cases",
    content:
      "The most important failure cases include Darth Vader being returned as an answer for a Harry Potter question, Harry being returned for a nuclear reactor question, and characters being returned instead of magical objects or creatures. These cases show the need for answer validation.",
  },
  {
    title: "Technical recommendation",
    content:
      "The most important improvement is to add an Answer Validator between LLM generation and supervisor aggregation. This validator should check whether named entities, objects and concepts in the final answer are actually supported by the retrieved context.",
  },
];

const Scenarios = () => {
  const [selectedScenarioId, setSelectedScenarioId] = useState("hallucination");

  const scenario = scenarios.find((item) => item.id === selectedScenarioId);
  const maxTime = Math.max(...scenario.variants.map((item) => item.time));
  const maxConfidence = 0.8;
  const maxScore = 100;

  return (
    <div className="scenarios-container">
      <section className="scenarios-header-card">
        <h2>Scenarios Evaluation</h2>
        <p>
          This section presents benchmark scenarios for MultiRAG model comparison,
          reranker impact analysis, hallucination resistance and evaluation metrics.
        </p>
      </section>

      <section className="scenario-card">
        <h3>1. Scenario selection</h3>

        <label htmlFor="scenario-select">Choose test scenario</label>
        <select
          id="scenario-select"
          value={selectedScenarioId}
          onChange={(event) => setSelectedScenarioId(event.target.value)}
        >
          {scenarios.map((item) => (
            <option key={item.id} value={item.id}>
              {item.title}
            </option>
          ))}
        </select>
      </section>

      <section className="scenario-card">
        <h3>2. Scenario description</h3>

        <div className="scenario-description-grid">
          <div>
            <strong>Scenario</strong>
            <p>{scenario.title}</p>
          </div>

          <div>
            <strong>Question</strong>
            <p>{scenario.question}</p>
          </div>

          <div>
            <strong>Goal</strong>
            <p>{scenario.goal}</p>
          </div>
        </div>
      </section>

      <section className="scenario-card">
        <h3>3. Side-by-side model comparison</h3>

        <div className="model-comparison-grid">
          {scenario.variants.map((variant) => (
            <div key={variant.name} className="model-result-card">
              <div className="model-card-header">
                <h4>{variant.name}</h4>
                <span className={`result-badge ${variant.result.toLowerCase()}`}>
                  {variant.result}
                </span>
              </div>

              <p><strong>Model:</strong> {variant.model}</p>
              <p><strong>Reranker:</strong> {variant.reranker}</p>
              <p><strong>Answer:</strong></p>
              <div className="answer-box">{variant.answer}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="scenario-card">
        <h3>4. Evaluation metrics</h3>

        <table>
          <thead>
            <tr>
              <th>Variant</th>
              <th>Pass / Fail</th>
              <th>Score</th>
              <th>Confidence</th>
              <th>Response time</th>
            </tr>
          </thead>
          <tbody>
            {scenario.variants.map((variant) => (
              <tr key={variant.name}>
                <td>{variant.name}</td>
                <td>{variant.result}</td>
                <td>{variant.score}/100</td>
                <td>{variant.confidence}</td>
                <td>{variant.time}s</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section className="scenario-card">
        <h3>5. Charts</h3>

        <div className="charts-grid">
          <SimpleBarChart
            title="Response time"
            axisY="Response time [s]"
            axisX="System configuration"
            data={scenario.variants}
            dataKey="time"
            maxValue={maxTime}
            suffix="s"
          />

          <SimpleBarChart
            title="Confidence score"
            axisY="Confidence"
            axisX="System configuration"
            data={scenario.variants}
            dataKey="confidence"
            maxValue={maxConfidence}
            suffix=""
          />

          <SimpleBarChart
            title="Evaluation score"
            axisY="Score [%]"
            axisX="System configuration"
            data={scenario.variants}
            dataKey="score"
            maxValue={maxScore}
            suffix="%"
          />
        </div>
      </section>

      <section className="scenario-card">
        <h3>6. Conclusion</h3>
        <p>{scenario.conclusion}</p>

        <p>
          Main technical recommendation: add an <strong>Answer Validator</strong> after
          LLM generation and before supervisor aggregation.
        </p>

        <pre className="scenario-code-block">
{`retrieval → reranking → prompt selection → LLM answer → answer validation → supervisor aggregation`}
        </pre>
      </section>

      <section className="scenario-card">
        <h3>7. Experimental Report</h3>

        <p>
          This section summarizes the benchmark, reranker impact, hallucination
          analysis, retrieval and generation errors, supervisor behavior, prompt
          quality and technical recommendations.
        </p>

        <div className="report-sections">
          {reportSections.map((section) => (
            <details key={section.title} className="report-details">
              <summary>{section.title}</summary>
              <p>{section.content}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  );
};

const SimpleBarChart = ({ title, axisY, axisX, data, dataKey, maxValue, suffix }) => {
  return (
    <div className="simple-chart-card">
      <h4>{title}</h4>
      <div className="chart-axis-y">{axisY}</div>

      <div className="simple-chart">
        {data.map((item) => {
          const value = item[dataKey];
          const height = Math.max((value / maxValue) * 180, value === 0 ? 4 : 10);

          return (
            <div className="simple-chart-bar-group" key={item.name}>
              <div className="simple-chart-value">
                {value}
                {suffix}
              </div>

              <div className="simple-chart-bar-wrapper">
                <div
                  className="simple-chart-bar"
                  style={{ height: `${height}px` }}
                />
              </div>

              <div className="simple-chart-label">{item.name}</div>
            </div>
          );
        })}
      </div>

      <div className="chart-axis-x">{axisX}</div>
    </div>
  );
};

export default Scenarios;
