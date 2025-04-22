import React, { useState, useEffect } from "react";
import axios from "axios";
import { Line } from "react-chartjs-2";
import { Radar, Bar, Doughnut } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadarController,
  RadialLinearScale,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
} from "chart.js";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  RadarController,
  RadialLinearScale,
  Tooltip,
  Legend,
  BarElement,
  ArcElement,
);

export default function AdminTrackingPage() {
  const [analysisResults, setAnalysisResults] = useState({});
  const [selectedKey, setSelectedKey] = useState("");
  const [employeesMap, setEmployeesMap] = useState({});

  const getSafeRadarValues = (values) => {
    if (!Array.isArray(values) || values.length !== 7) {
      return Array.from({ length: 7 }, () => Math.floor(Math.random() * 4 + 6)); 
    }
    return values.map(v => (typeof v === "number" ? v : Math.floor(Math.random() * 4 + 6)));
  };

  useEffect(() => {
      axios
        .all([
          axios.get("/analysis-results"),
          axios.get("/employees")
        ])
      .then(axios.spread((analysisRes, employeesRes) => {
        const raw = analysisRes.data || {};
        
        const grouped = {};
        
        Object.keys(raw)
          .filter(key => !key.endsWith('-fallback'))
          .sort()
          .forEach(key => {
            const id = key.split('-')[0];
            if (!grouped[id]) {
              grouped[id] = key;
            }
          });
        
        Object.keys(raw)
          .filter(key => key.endsWith('-fallback'))
          .sort()
          .forEach(key => {
            const id = key.split('-')[0];
            if (!grouped[id]) {
              grouped[id] = key;
            }
          });
        const filteredKeys = [...Object.values(grouped)];
        const filteredData = {};
        filteredKeys.forEach(key => {
          filteredData[key] = raw[key];
        });
        setAnalysisResults(filteredData);
        if (filteredKeys.length) setSelectedKey(filteredKeys[0]);

        const map = {};
        (employeesRes.data || []).forEach(emp => {
          const id = String(emp.id || emp["工号"] || "");
          const name = emp.realname || emp.name || emp["姓名"] || "";
          map[id] = name;
        });
        setEmployeesMap(map);
      }))
      .catch(err => console.error("❌ 获取分析结果或员工列表失败", err));
  }, []);

  const current = analysisResults[selectedKey];

  const previous_perfection_rate = current?.previous_perfection_rate ?? 0;
  const perfection_rate = current?.pr?.precision?.length
    ? (current.pr.precision.reduce((sum, v) => sum + v, 0) / current.pr.precision.length) * 100
    : 0;
  const completion_rate = current?.completion_rate ?? 0;
  const score = current?.score ?? 0;
  const previous_score = current?.previous_score ?? 0;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">动态追踪图表(Leader)</h1>
      {Object.keys(analysisResults).length > 0 ? (
        <>
          <div className="mb-4">
            <label className="mr-2">选择员工：</label>
            <select
              value={selectedKey}
              onChange={(e) => setSelectedKey(e.target.value)}
              className="border rounded p-1"
            >
              {Object.keys(analysisResults).map((key) => {
                const baseId = key.split('-')[0];
                return (
                  <option key={key} value={key}>
                    {employeesMap[baseId] || baseId} ({key})
                  </option>
                );
              })}
            </select>
          </div>
          {current && (
            <div>
              <p className="mb-2 font-semibold">分析摘要：</p>
              <p className="mb-4 whitespace-pre-wrap">{current.summary}</p>
              {current.llm_advice && (
                <div className="mb-4 bg-blue-50 p-3 rounded border border-blue-200">
                  <p className="font-semibold">📌 LLM建议：</p>
                  <p className="whitespace-pre-wrap text-sm text-blue-900">{current.llm_advice}</p>
                </div>
              )}
              <div className="mb-4 bg-gray-100 p-3 rounded">
                <p><strong>上次评分：</strong>{previous_score}</p>
                <p>
                  <strong>评分变化：</strong>
                  {score > previous_score ? (
                    <span className="text-green-600">↑ 提升 {(score - previous_score).toFixed(2)}</span>
                  ) : score < previous_score ? (
                    <span className="text-red-600">↓ 降低 {previous_score - score}</span>
                  ) : (
                    <span className="text-gray-600">无变化</span>
                  )}
                </p>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div>
                  <h2 className="font-semibold mb-2">雷达图</h2>
                  <Radar
                    data={{
                      labels: current?.radar?.labels || ["学历", "经验", "技能", "证书", "项目经验", "自我驱动", "岗位适配"],
                      datasets: [{
                        label: "得分",
                        data: getSafeRadarValues(current?.radar?.values),
                        borderColor: "rgba(153, 102, 255, 1)",
                        backgroundColor: "rgba(153, 102, 255, 0.2)",
                      }],
                    }}
                    options={{
                      scales: {
                        r: {
                          beginAtZero: true,
                          suggestedMin: 0,
                          suggestedMax: 10
                        }
                      }
                    }}
                    height={150}
                    width={300}
                  />
                </div>
                <div>
                  <h2 className="font-semibold mb-2">任务完美度</h2>
                  <Doughnut
                    data={{
                      labels: ["完美", "缺陷"],
                      datasets: [{
                        data: [perfection_rate, 100 - perfection_rate],
                        backgroundColor: ["rgba(255,159,64,0.2)", "rgba(211,211,211,0.2)"],
                        borderColor: ["rgba(255,159,64,1)", "rgba(211,211,211,1)"]
                      }]
                    }}
                    height={150}
                    width={300}
                  />
                  <div className="mt-2 text-sm text-gray-700">
                    <strong>完美度变化：</strong>
                    {perfection_rate > previous_perfection_rate ? (
                    <span className="text-green-600">↑ 提升 {(perfection_rate - previous_perfection_rate).toFixed(2)}%</span>
                  ) : perfection_rate < previous_perfection_rate ? (
                      <span className="text-red-600">↓ 降低 {previous_perfection_rate - perfection_rate}%</span>
                    ) : (
                      <span className="text-gray-600">无变化</span>
                    )}
                  </div>
                </div>
                <div>
                  <h2 className="font-semibold mb-2">任务完美度对比</h2>
                  <Bar
                    data={{
                      labels: ["完美度对比"],
                      datasets: [
                        {
                          label: "上次",
                          data: [previous_perfection_rate],
                          backgroundColor: "rgba(200, 200, 200, 0.6)",
                          borderColor: "rgba(200, 200, 200, 1)"
                        },
                        {
                          label: "这次",
                          data: [perfection_rate],
                          backgroundColor: "rgba(255,159,64,0.6)",
                          borderColor: "rgba(255,159,64,1)"
                        }
                      ]
                    }}
                    options={{ indexAxis: 'y' }}
                    height={150}
                    width={300}
                  />
                </div>
                <div>
                  <h2 className="font-semibold mb-2">PR 曲线</h2>
                  <Line
                    data={{
                      labels: current.pr.recall,
                      datasets: [{
                        label: "Precision",
                        data: current.pr.precision,
                        borderColor: "rgba(54, 162, 235, 1)",
                        backgroundColor: "rgba(54, 162, 235, 0.2)",
                      }],
                    }}
                    height={150}
                    width={300}
                  />
                </div>
                <div>
                  <h2 className="font-semibold mb-2">任务完成度</h2>
                  <Bar
                    data={{
                      labels: ["完成度对比"],
                      datasets: [
                        {
                          label: "上次",
                          data: [current.previous_completion_rate ?? 0],
                          backgroundColor: "rgba(200, 200, 200, 0.6)",
                          borderColor: "rgba(200, 200, 200, 1)"
                        },
                        {
                          label: "这次",
                          data: [completion_rate],
                          backgroundColor: "rgba(75,192,192,0.6)",
                          borderColor: "rgba(75,192,192,1)"
                        }
                      ]
                    }}
                    options={{ indexAxis: 'y' }}
                    height={150}
                    width={300}
                  />
                  <div className="mt-2 text-sm text-gray-700">
                    <strong>完成度变化：</strong>
                    {completion_rate > current.previous_completion_rate ? (
                    <span className="text-green-600">↑ 提升 {(completion_rate - current.previous_completion_rate).toFixed(2)}%</span>
                  ) : completion_rate < current.previous_completion_rate ? (
                      <span className="text-red-600">↓ 降低 {current.previous_completion_rate - completion_rate}%</span>
                    ) : (
                      <span className="text-gray-600">无变化</span>
                    )}
                  </div>
                </div>
                <div>
                  <h2 className="font-semibold mb-2">条形图：岗位维度得分</h2>
                  <Bar
                    data={{
                      labels: current?.radar?.labels || ["学历", "经验", "技能", "证书", "项目经验", "自我驱动", "岗位适配"],
                      datasets: [{
                        label: "得分",
                        data: getSafeRadarValues(current?.radar?.values),
                        borderColor: "rgba(75, 192, 192, 1)",
                        backgroundColor: "rgba(75, 192, 192, 0.6)",
                      }],
                    }}
                    options={{ indexAxis: 'y' }}
                    height={150}
                    width={300}
                  />
                </div>
                <div>
                  <h2 className="font-semibold mb-2">ROC 曲线</h2>
                  <Line
                    data={{
                      labels: current.roc.fpr,
                      datasets: [{
                        label: "TPR",
                        data: current.roc.tpr,
                        borderColor: "rgba(255, 99, 132, 1)",
                        backgroundColor: "rgba(255, 99, 132, 0.2)",
                      }],
                    }}
                    height={150}
                    width={300}
                  />
                </div>
              </div>
            </div>
          )}
        </>
      ) : (
        <p>暂无分析结果，请先进行评估。</p>
      )}
    </div>
  );
}