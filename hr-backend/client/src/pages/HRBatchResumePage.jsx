import React, { useState } from "react";
import axios from "axios";

export default function HRBatchResumePage() {
  const [resumeList, setResumeList] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [recommendedSet, setRecommendedSet] = useState(new Set());
  const [fileMap, setFileMap] = useState({});

  const handleUpload = async (e) => {
    const rawFiles = Array.from(e.target.files);
    const files = rawFiles.filter(
      file =>
        !file.name.startsWith('.') &&
        /\.(pdf|docx)$/i.test(file.name)
    );

    if (files.length === 0) {
      alert("❌ 没有有效的简历文件（仅支持 .pdf 和 .docx）");
      return;
    }

    const formData = new FormData();
    const newFileMap = {};
    files.forEach((file) => {
      formData.append("files", file);
      newFileMap[file.name.replace(/\.(pdf|docx?)$/, "")] = file;
    });

    setFileMap(newFileMap);
    setUploading(true);

    try {
      const res = await axios.post("/batch-analyze-resumes-brief", formData);
      const summary = Array.isArray(res.data) ? res.data : [];

      if (!summary.length) {
        console.warn("⚠️ 后端返回空数组或无数据", res);
        alert("❌ 没有分析出任何简历，请检查文件内容是否规范");
      }

      console.log("🧩 返回原始数据：", res);
      setResumeList(summary);
      console.log("🧩 后端返回 summary：", summary);
    } catch (err) {
      console.error("❌ 上传失败：", err);
      alert("❌ 上传失败：" + (err?.response?.data?.detail || err.message || "服务器无响应"));
    } finally {
      setUploading(false);
    }
  };

  const handleRecommend = async (item) => {
    if (recommendedSet.has(item.resume_id)) return;

    const pureName = item.name?.split("/").pop();
    let fileToUse = fileMap[pureName];

    if (!fileToUse) {
      const possibleKey = Object.keys(fileMap).find((key) => key.includes(pureName));
      if (possibleKey) fileToUse = fileMap[possibleKey];
    }

    if (!fileToUse) {
      alert("未找到对应简历文件，无法保存 PDF");
      return;
    }

    const reader = new FileReader();
    reader.onload = async () => {
      try {
        const payload = {
          ...item,
          pdf_base64: reader.result.split(",")[1],
        };
        await axios.post("/recommend", payload);
        alert(`✅ 已加入人才储备库：${item.name}`);
        setRecommendedSet(new Set([...recommendedSet, item.resume_id]));
      } catch (err) {
        alert("❌ 加入人才库失败");
        console.error(err);
      }
    };
    reader.readAsDataURL(fileToUse);
  };

  return (
    <div style={{ padding: "24px" }}>
      <h2>📥 批量简历分析</h2>
      <div style={{ marginBottom: "12px" }}>
        <label htmlFor="resumeUpload">📂 可多选文件或整个文件夹上传：</label><br />
        <input
          id="resumeUpload"
          type="file"
          multiple
          webkitdirectory=""
          accept=".pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          onChange={handleUpload}
          disabled={uploading}
        />
      </div>

      {resumeList.length > 0 && (
        <table border="1" cellPadding="8" style={{ width: "100%", marginTop: "16px", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th>简历编号</th>
              <th>姓名</th>
              <th>评分</th>
              <th>学历</th>
              <th>证书</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {resumeList.filter(item => item && item.resume_id).map((item) => (
              <tr key={item.resume_id}>
                <td>{item.resume_id}</td>
                <td>{item.name || "未命名"}</td>
                <td>{item.score ?? "无"}</td>
                <td>{item["学历_x"] ?? "无"}</td>
                <td>{item["证书数_x"] ?? "无"}</td>
                <td>
                  <button
                    onClick={() => handleRecommend(item)}
                    disabled={recommendedSet.has(item.resume_id)}
                  >
                    {recommendedSet.has(item.resume_id) ? "✅ 已加入" : "📥 加入人才储备库"}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}