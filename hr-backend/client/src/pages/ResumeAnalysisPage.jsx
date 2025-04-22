import React, { useState } from 'react';
import axios from 'axios';

const ResumeAnalysisPage = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [chatPrompt, setChatPrompt] = useState("");
  const [chatResponse, setChatResponse] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [recommendReason, setRecommendReason] = useState("");

  const handleUpload = async () => {
    if (!file) return alert('请先选择一个简历文件');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const res = await axios.post('/api/analyze-resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        withCredentials: true
      });
      if (!res.data || !res.data.resume_id || res.data.score === undefined) {
        alert("❌ 返回数据不完整，请检查简历格式或稍后重试");
        setLoading(false);
        return;
      }
      console.log("✅ 后端响应数据：", res.data);

      const generatedId = res.data.resume_id;

      setResult({
        resume_id: generatedId,
        score: res.data.score,
        recommended_position: res.data.recommended_position,
        analysis: res.data.analysis
      });

      await axios.post("/api/save-resume", {
        resume_id: generatedId,
        score: res.data.score,
        recommended_position: res.data.recommended_position,
        analysis: res.data.analysis
      });
    } catch (err) {
      console.error('❌ 上传失败', err);
      alert('上传失败，请检查后端是否已启动');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToPool = () => {
    if (!result) return;
    const now = new Date();
    const newEntry = {
      id: `${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}-${Date.now() % 1000}`,
      resume_id: result.resume_id,
      name: result.name || '未知',
      skills: result.recommended_position || '未知',
      score: result.score,
      recommender: localStorage.getItem('username') || 'HR用户',
      addedAt: now.toISOString().slice(0, 10)
    };
    console.log("📥 加入人才库：", newEntry);
    alert("✅ 已加入人才储备库！");
  };

  return (
    <>
      <div style={{ padding: 50 }}>
        <h1 style={{ marginBottom: 20 }}>📄 简历智能分析（HR）</h1>

        <input
          type="file"
          accept=".pdf,.docx"
          onChange={(e) => setFile(e.target.files[0])}
        />
        <br /><br />
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <button
            onClick={handleUpload}
            disabled={loading}
            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition shadow"
          >
            {loading ? '分析中...' : '上传并分析简历'}
          </button>
          <button
            onClick={async () => {
              const inputId = prompt("请输入简历编号（格式如：2025-04-123--1）：");
              if (inputId) {
                setLoading(true);
                try {
                  
                  let fetchRes = await axios.get(`/api/get-resume/${inputId}`);
                  var data = fetchRes.data;
                } catch (err) {
                  
                  if (err.response && err.response.status === 404) {
                    alert("❌ 未找到报告，请确认编号或稍后再试");
                    console.error(err);
                    setLoading(false);
                    return;
                  }
                }

                
                if (!data) data = {};
                if (!data.resume_id || data.score === undefined) {
                  alert("❌ 返回数据不完整，无法展示分析");
                  setLoading(false);
                  return;
                }
                setResult({
                  resume_id: data.resume_id,
                  score: parseFloat(data.score ?? 0),
                  recommended_position: data.recommended_position || "无推荐",
                  analysis: typeof data.analysis === "string"
                    ? data.analysis
                    : JSON.stringify(data.analysis, null, 2)
                });

                
                await axios.post("/api/save-resume", {
                  resume_id: data.resume_id,
                  score: data.score,
                  recommended_position: data.recommended_position,
                  analysis: data.analysis
                });
                setLoading(false);
              }
            }}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition shadow"
          >
            🔍 通过编号查询
          </button>
        </div>

        {loading && (
          <div style={{ marginTop: 30, fontSize: 16, color: '#555' }}>
            ⏳ 正在分析简历，请稍候...
          </div>
        )}
        {result && (
          <div style={{ marginTop: 40 }}>
            <h2>分析结果 ✅</h2>
            <p><strong>编号：</strong>{result.resume_id}</p>
            <p><strong>评分：</strong>{String(result.score)} 分</p>
            <p><strong>推荐岗位：</strong>{String(result.recommended_position)}</p>
            <h3>LLM 报告：</h3>
            <pre style={{
              background: '#f0f0f0',
              padding: 20,
              whiteSpace: 'pre-wrap',
              wordWrap: 'break-word',
              borderRadius: 4
            }}>
              {typeof result.analysis === 'string'
                ? result.analysis
                : JSON.stringify(result.analysis, null, 2)}
            </pre>
            <div style={{ marginTop: 20 }}>
              <button
                onClick={handleAddToPool}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700 transition shadow"
              >
                加入人才储备库
              </button>
            </div>
          </div>
        )}
        <div style={{ marginTop: 40 }}>
          <h2>LLM 面试助手 🤖</h2>
          <textarea
            rows={3}
            value={chatPrompt}
            onChange={(e) => setChatPrompt(e.target.value)}
            placeholder="请输入你的面试辅助提问（如：候选人说他熟悉C++但没有项目经验，如何提问，是否适合后端岗位）"
            style={{ width: '100%', padding: 10, borderRadius: 4, borderColor: '#ccc' }}
          />
          <button
            onClick={async () => {
              if (!chatPrompt.trim()) return alert("请输入问题");
              setChatLoading(true);
              try {
                const res = await axios.post("/api/interview-assist", {
                  resume_id: result?.resume_id,
                  prompt: chatPrompt
                });
                setChatResponse(res.data.response);
              } catch (err) {
                setChatResponse("❌ 面试助手调用失败，请稍后再试");
                console.error(err);
              } finally {
                setChatLoading(false);
              }
            }}
            className="bg-orange-600 text-white px-4 py-2 rounded hover:bg-orange-700 transition shadow"
            style={{ marginTop: 10 }}
          >
            {chatLoading ? "分析中..." : "📎 向面试助手提问"}
          </button>
          {chatResponse && (
            <pre style={{ background: "#fefefe", padding: 16, marginTop: 10, border: "1px solid #ccc", borderRadius: 4 }}>
              {chatResponse}
            </pre>
          )}
        </div>
        <div style={{ marginTop: 40 }}>
          <h2>📝 推荐入职</h2>
          <button
            onClick={async () => {
              const reason = prompt("请输入推荐理由：");
              if (!reason || !result) return;

              try {
                let finalResult = result;

                
                try {
                  const res = await axios.get(`/api/get-resume/${result.resume_id}`);
                  finalResult = res.data;
                } catch (err) {
                  if (err.response && err.response.status === 404) {
                    if (result.resume_id.endsWith("-1")) {
                      const formData = new FormData();
                      formData.append('file', file);
                      const analysisRes = await axios.post("/api/analyze-resume", formData, {
                        headers: { 'Content-Type': 'multipart/form-data' }
                      });
                      finalResult = {
                        resume_id: analysisRes.data.resume_id + "-1",
                        score: analysisRes.data.score,
                        recommended_position: analysisRes.data.recommended_position,
                        analysis: analysisRes.data.analysis
                      };
                    } else {
                      const analysisRes = await axios.post("/api/refresh-resume", { resume_id: result.resume_id });
                      finalResult = analysisRes.data;
                    }

                    await axios.post("/api/recommend-employee", {
                      resume_id: finalResult.resume_id,
                      reason,
                      analysis: finalResult.analysis,
                      recommended_position: finalResult.recommended_position || "待定",
                      score: finalResult.score || 0
                    });

                    alert("✅ 推荐已发送给上级审批！");
                  }
                }
              } catch (err) {
                console.error(err);
                alert("❌ 推荐提交失败，请稍后再试");
              }
            }}
            className="bg-cyan-600 text-white px-4 py-2 rounded hover:bg-cyan-700 transition shadow"
          >
            📤 推荐入职（提交至上级审批）
          </button>
        </div>
      </div>
    </>
  );
}

export default ResumeAnalysisPage;