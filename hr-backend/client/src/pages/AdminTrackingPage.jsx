import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { Line } from "react-chartjs-2";
import { Radar, Bar, Doughnut } from "react-chartjs-2";
import anime from "animejs";
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
  Filler,
} from "chart.js";
import { Chart } from "chart.js";

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
  Filler,
);

export default function AdminTrackingPage() {
  const [analysisResults, setAnalysisResults] = useState({});
  const [selectedKey, setSelectedKey] = useState("");
  const [employeesMap, setEmployeesMap] = useState({});
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const prRef = useRef(null);

  const getRadarValues = (key) => {
    const main = analysisResults[key];
    const vals = main?.radar?.values || [];
    return vals.length === 7 ? vals : [0, 0, 0, 0, 0, 0, 0];
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const [analysisRes, employeesRes] = await Promise.all([
          axios.get("/analysis-results"),
          axios.get("/employees"),
        ]);

        // 处理分析结果
        const data = analysisRes.data || {};
        if (!data || Object.keys(data).length === 0) {
          throw new Error("没有可用的分析结果数据");
        }
        setAnalysisResults(data);
        const keys = Object.keys(data);
        if (keys.length) setSelectedKey(keys[0]);

        // 构建员工 ID -> 姓名 映射
        const map = {};
        const employeesRaw = employeesRes.data;
        const employeeList = Array.isArray(employeesRaw)
           ? employeesRaw
            : Array.isArray(employeesRaw?.data)
            ? employeesRaw.data
    : [];

employeeList.forEach(emp => {
  const id = String(emp.id || emp["工号"] || "");
  const name = emp.realname || emp.name || emp["姓名"] || "";
  map[id] = name;
});
setEmployeesMap(map);
      } catch (err) {
        console.error("❌ 获取数据失败", err);
        setError(err.response?.data?.message || err.message || "获取数据失败，请稍后重试");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const current = analysisResults[selectedKey];

  function calculateAUC(fpr, tpr) {
    let auc = 0;
    for (let i = 1; i < fpr.length; i++) {
      const width = fpr[i] - fpr[i - 1];
      const height = (tpr[i] + tpr[i - 1]) / 2;
      auc += width * height;
    }
    return auc;
  }

  useEffect(() => {
    if (current?.roc?.fpr && current?.roc?.tpr) {
      const aucValue = current?.roc?.auc ?? calculateAUC(current.roc.fpr, current.roc.tpr);
      const el = document.getElementById("auc-value");
      if (el) {
        anime({
          targets: el,
          keyframes: [
            { innerHTML: 0 },
            { innerHTML: parseFloat(aucValue.toFixed(2)) }
          ],
          easing: 'linear',
          round: 2,
          duration: 1500,
        });
      }
    }
  }, [current]);

  useEffect(() => {
    if (current?.pr?.precision && current?.pr?.recall) {
      const precision = current.pr.precision;
      const recall = current.pr.recall;
      const f1Scores = precision.map((p, i) => {
        const r = recall[i];
        return (2 * p * r) / (p + r + 1e-6);
      });
      const maxIdx = f1Scores.indexOf(Math.max(...f1Scores));
      const displayPoint = `平衡点 (R=${recall[maxIdx].toFixed(2)}, P=${precision[maxIdx].toFixed(2)})`;

      const el = document.getElementById("pr-balance");
      if (el) {
        el.innerText = displayPoint;
        anime({
          targets: el,
          opacity: [0, 1],
          translateY: [-10, 0],
          duration: 1200,
          easing: 'easeOutExpo',
          delay: 1000
        });
      }
    }
  }, [current]);

  function animateAUCOverlay() {
    const canvasWrapper = document.querySelector('#roc-line canvas');
    if (!canvasWrapper) {
      console.warn("❗ 未找到 ROC 图表画布");
      return;
    }
    const ctx = canvasWrapper.getContext('2d');
    const width = canvasWrapper.width;
    const height = canvasWrapper.height;

    let progress = 0;
    function draw(progress) {
      ctx.clearRect(0, 0, width, height);
      Chart.getChart("roc-line")?.update("none");
      if (progress === 0) return;
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, width * progress, height);
      ctx.clip();
      ctx.fillStyle = "rgba(255, 99, 132, 0.2)";
      ctx.fillRect(0, 0, width, height);
      ctx.restore();
    }

    function step() {
      if (progress < 1) {
        progress += 0.0007;
        draw(progress);
        setTimeout(() => {
          requestAnimationFrame(step);
        }, 30);
      }
    }

    console.log("🎯 开始填充动画");
    draw(0); 
    step();
  }

  
  let prPrecision = [], prRecall = [], prBestIdx = -1;
  if (current?.pr?.precision && current?.pr?.recall) {
    prPrecision = current.pr.precision;
    prRecall = current.pr.recall;
    const f1Scores = prPrecision.map((p, i) => {
      const r = prRecall[i];
      return (2 * p * r) / (p + r + 1e-6);
    });
    prBestIdx = f1Scores.indexOf(Math.max(...f1Scores));
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">动态追踪图表</h1>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">错误：</strong>
          <span className="block sm:inline">{error}</span>
          <button 
            className="absolute top-0 bottom-0 right-0 px-4 py-3"
            onClick={() => setError(null)}
          >
            <span className="sr-only">关闭</span>
            <svg className="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ) : Object.keys(analysisResults).length > 0 ? (
        <>
          <div className="mb-4">
            <label className="mr-2">选择员工：</label>
            <select
              value={selectedKey}
              onChange={(e) => setSelectedKey(e.target.value)}
              className="border rounded p-1"
            >
              {Object.keys(analysisResults).map((key) => (
                <option key={key} value={key}>
                  {`${employeesMap[key.split('-')[0]] || key.split('-')[0]} (${key})`}
                </option>
              ))}
            </select>
          </div>
          {current && (
            <div>
              <p className="mb-2 font-semibold">分析摘要：</p>
              <p className="mb-4 whitespace-pre-wrap">{current.summary}</p>
              <motion.div
                className="mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <h2 className="font-semibold mb-2">ROC 曲线</h2>
                <button
                  onClick={() => {
                    animateAUCOverlay();
                  }}
                  className="mb-2 px-3 py-1 bg-pink-500 text-white rounded hover:bg-pink-600 transition"
                >

                </button>
                <Line
                  id="roc-line"
                  data={{
                    labels: current.roc.fpr,
                    datasets: [{
                      label: "TPR",
                      data: current.roc.tpr,
                      borderColor: "rgba(255, 99, 132, 1)",
                      backgroundColor: "rgba(255, 99, 132, 0.2)",
                      fill: true,
                    }],
                  }}
                  options={{
                    animation: { duration: 0 },
                    onHover: (event, chartElement) => {
                      if (chartElement.length) {
                        animateAUCOverlay();
                      }
                    },
                  }}
                />
                <span id="auc-value" className="text-lg font-bold text-pink-600 mt-2 block">AUC: 0.00</span>
              </motion.div>
              <motion.div
                className="mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <h2 className="font-semibold mb-2">PR 曲线</h2>
                <Line
                  ref={prRef}
                  data={{
                    labels: prRecall,
                    datasets: [
                      {
                        label: "Precision-Recall",
                        data: prPrecision,
                        borderColor: "rgba(54, 162, 235, 1)",
                        backgroundColor: "rgba(54, 162, 235, 0.15)",
                        fill: true,
                        pointRadius: 0,
                        tension: 0.1,
                      },
                      {
                        label: "Best F1 Point",
                        data: prRecall.map((_, i) =>
                          i === prBestIdx ? prPrecision[i] : null
                        ),
                        backgroundColor: "rgba(255, 99, 132, 1)",
                        borderColor: "rgba(255, 99, 132, 1)",
                        pointRadius: 6,
                        showLine: false,
                      },
                    ],
                  }}
                  options={{
                    responsive: true,
                    plugins: {
                      legend: { display: false },
                      tooltip: { enabled: true },
                    },
                    scales: {
                      x: { title: { display: true, text: "Recall" } },
                      y: { title: { display: true, text: "Precision" } },
                    },
                  }}
                />
                <span id="pr-balance" className="text-sm mt-2 text-blue-600 block">平衡点 F1 最佳</span>
              </motion.div>
              <motion.div
                className="mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <h2 className="font-semibold mb-2">雷达图</h2>
                <Radar
                  data={{
                    labels: current.radar.labels,
                    datasets: [{
                      label: "得分",
                      data: getRadarValues(selectedKey),
                      borderColor: "rgba(153, 102, 255, 1)",
                      backgroundColor: "rgba(153, 102, 255, 0.2)",
                    }],
                  }}
                  options={{
                    animation: { duration: 2000, easing: 'easeOutElastic' }
                  }}
                />
              </motion.div>
              <motion.div
                className="mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <h2 className="font-semibold mb-2">条形图：岗位维度得分</h2>
                <Bar
                  data={{
                    labels: current.radar.labels,
                    datasets: [{
                      label: "得分",
                      data: getRadarValues(selectedKey),
                      borderColor: "rgba(75, 192, 192, 1)",
                      backgroundColor: "rgba(75, 192, 192, 0.6)",
                    }],
                  }}
                  options={{
                    indexAxis: 'y',
                    animation: { duration: 2000, easing: 'easeOutBounce' },
                  }}
                />
              </motion.div>
              <motion.div
                className="mb-6"
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              >
                <h2 className="font-semibold mb-2">环形图：平均精准率 vs 平均召回率</h2>
                <Doughnut
                  data={{
                    labels: ["平均精准率", "平均召回率"],
                    datasets: [{
                      data: [
                        current.pr.precision.reduce((a, b) => a + b, 0) / current.pr.precision.length,
                        current.pr.recall.reduce((a, b) => a + b, 0) / current.pr.recall.length,
                      ],
                      backgroundColor: [
                        "rgba(255, 206, 86, 0.2)",
                        "rgba(75, 192, 192, 0.2)"
                      ],
                      borderColor: [
                        "rgba(255, 206, 86, 1)",
                        "rgba(75, 192, 192, 1)"
                      ],
                    }],
                  }}
                  options={{
                    animation: { animateRotate: true, duration: 2000, easing: 'easeInOutCubic' }
                  }}
                />
              </motion.div>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500">暂无分析结果，请先进行评估。</p>
        </div>
      )}
    </div>
  );
}