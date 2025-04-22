import React, { useEffect, useState } from "react";
import axios from "axios";

export default function TaskScorePage() {
  const [tasks, setTasks] = useState([]);
  const [scores, setScores] = useState({});
  const [comments, setComments] = useState({});
  const [visible, setVisible] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    axios.get("/tasks")
      .then(res => {
        setTasks(res.data || []);
        const scoreMap = {};
        const commentMap = {};
        (res.data || []).forEach(t => {
          if (t.status === "已评分") {
            scoreMap[t.id] = t.score;
            commentMap[t.id] = t.comment;
          }
        });
        setScores(scoreMap);
        setComments(commentMap);
      })
      .catch(err => console.error("❌ 获取任务失败", err));
  }, []);

  const handleScoreChange = (taskId, value) => {
    setScores(prev => ({ ...prev, [taskId]: value }));
  };

  const handleCommentChange = (taskId, value) => {
    setComments(prev => ({ ...prev, [taskId]: value }));
  };

  const handleSubmitScore = async (taskId) => {
    try {
      const score = scores[taskId];
      const comment = comments[taskId] || "";
      if (!score) {
        alert("请输入评分");
        return;
      }
      console.log("🚀 提交评分：", { task_id: taskId, score, comment });
      setLoading(true);
      const res = await axios.post("/task/score", {
        task_id: taskId,
        score: Number(score),
        comment: comment
      }, {
        withCredentials: true
      });
      console.log("✅ 评分成功，已保存并触发后端分析：", res.data);
      setLoading(false);
      setTasks(prev =>
        prev.map(t =>
          t.id === taskId
            ? { ...t, score: score, comment: comment, status: "已评分" }
            : t
        )
      );
    } catch (err) {
      setLoading(false);
      console.error("❌ 评分失败原因：", err.response?.data || err.message);
      alert("❌ 评分失败");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
       <h1>项目打分页面（Leader）</h1>
      <button
        onClick={() => setVisible(!visible)}
        style={{
          marginBottom: "10px",
          padding: "8px 16px",
          backgroundColor: "#007bff",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer"
        }}
      >
        {visible ? "隐藏评分面板" : "打开评分面板"}
      </button>
      {visible && tasks.map(task => (
        <div key={task.id} style={{ border: "1px solid #ccc", padding: "10px", marginBottom: "10px" }}>
          <p><strong>姓名：</strong>{task.from_realname}</p>
          <p><strong>提交时间：</strong>{task.timestamp}</p>
          <p><strong>任务内容：</strong>{task.task}</p>
          <p><strong>当前状态：</strong>{task.status}</p>
          <input
            type="number"
            placeholder="请输入评分（1-10）"
            value={scores[task.id] || ""}
            onChange={(e) => handleScoreChange(task.id, e.target.value)}
            style={{ marginRight: "10px" }}
          />
          <textarea
            placeholder="请输入评价（选填）"
            value={comments[task.id] || ""}
            onChange={(e) => handleCommentChange(task.id, e.target.value)}
            style={{ width: "100%", marginBottom: "10px" }}
          />
          <button onClick={() => handleSubmitScore(task.id)}>提交评分</button>
        </div>
      ))}
      {loading && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: "rgba(0,0,0,0.3)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: "#fff",
            padding: "30px 50px",
            borderRadius: "8px",
            boxShadow: "0 0 10px rgba(0,0,0,0.3)",
            fontSize: "18px",
            fontWeight: "bold"
          }}>
            ⏳ 正在提交评分并分析中，请稍候...
          </div>
        </div>
      )}
    </div>
  );
}