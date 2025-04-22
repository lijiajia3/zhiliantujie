import React, { useState } from "react";
import axios from "axios";

export default function HRRecommend() {
  console.log("📋 HRRecommend 页面已加载");

  const [resumeId, setResumeId] = useState("");
  const [reason, setReason] = useState("");
  const [queryResumeId, setQueryResumeId] = useState("");
  const [canRecommendFromQuery, setCanRecommendFromQuery] = useState(false);
  const [analysis, setAnalysis] = useState("");

  const handleSubmit = async () => {
    try {
      const res = await axios.post("/recommend-to-admin", {
        resume_id: resumeId || undefined,
        reason,
        analysis
      });

      const generatedId = res.data?.data?.resume_id || "已生成";
      setResumeId(generatedId);
      alert(`推荐成功，等待主管审批！简历编号为：${generatedId}`);
      setReason("");
    } catch (err) {
      console.error("推荐失败：", err.response?.data || err.message || err);
      alert("推荐失败，请稍后重试");
    }
  };

  const handleQuery = async () => {
    if (!queryResumeId.trim()) return alert("请输入编号");
    try {
    const res = await axios.get(`/resume/analysis/${queryResumeId.trim()}`);
      const data = res.data;
      const analysis = data?.analysis || "无分析内容";
      setResumeId(queryResumeId.trim());
      setCanRecommendFromQuery(true);
      setAnalysis(analysis);
      alert(`分析报告（编号 ${queryResumeId}）：\n${analysis}`);
    } catch (err) {
      console.error("查询失败：", err.response?.data || err.message || err);
      alert("❌ 查询失败或未找到该编号");
    }
  };

  return (
    <>
      <div className="p-6 max-w-xl mx-auto">
        <h1 className="text-2xl font-bold mb-4">HR 推荐候选人</h1>
        <div className="mb-4">
          <label className="block mb-1 font-medium">简历编号（由系统自动生成）：</label>
          <div className="flex items-center">
            <span className="bg-gray-100 border border-r-0 p-2 rounded-l text-gray-600"></span>
            <input
              type="text"
              value={resumeId}
              onChange={(e) => setResumeId(e.target.value)}
              placeholder="编号"
              maxLength={3}
              className="border p-2 w-full rounded-r"
            />
          </div>
        </div>
        <div className="mb-4">
          <label className="block mb-1 font-medium">推荐理由：</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="border p-2 w-full rounded"
          />
        </div>
        <button
          onClick={handleSubmit}
          className="bg-blue-600 text-white px-6 py-2 rounded"
        >
          提交推荐
        </button>
        <hr className="my-6" />
        <div className="mb-4">
          <label className="block mb-1 font-medium">查询简历分析报告：</label>
          <input
            type="text"
            value={queryResumeId}
            onChange={(e) => setQueryResumeId(e.target.value)}
            placeholder="请输入完整编号（如 20250422-01-0）"
            className="border p-2 w-full rounded mb-2"
          />
          <div className="flex items-center space-x-4">
            <button
              onClick={handleQuery}
              className="bg-green-600 text-white px-4 py-2 rounded"
            >
              查询报告
            </button>
            {canRecommendFromQuery && (
              <button
                onClick={handleSubmit}
                className="bg-blue-500 text-white px-4 py-2 rounded"
              >
                推荐此人
              </button>
            )}
          </div>
          {canRecommendFromQuery && (
            <div className="mt-4 p-4 border rounded bg-gray-50">
              <h2 className="font-semibold mb-2">分析报告</h2>
              <pre className="whitespace-pre-wrap text-sm text-gray-800">{analysis}</pre>
            </div>
          )}
        </div>
      </div>
    </>
  );
}