
import React from "react";

export default function ContactPage() {
  return (
    <div style={{ padding: "40px", maxWidth: "800px", margin: "0 auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "28px", marginBottom: "20px" }}>联系我们</h1>
      <p style={{ fontSize: "16px", lineHeight: "1.8" }}>
        如果您对我们的产品有任何疑问，或希望进行合作与咨询，欢迎通过以下方式与我们取得联系：
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px" }}>
        📧 电子邮件：<a href="mailto:lijiaxuan@sxrjhc.cn">lijiaxuan@sxrjhc.cn</a><br />
        📞 电话：+86-131-1361-1578<br />
        🏢 地址：中国山西省太原市迎泽西大街国际能源中心 1412-1413
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px", color: '#888' }}>
        我们期待与您合作，共创智能人力资源管理新未来。
      </p>
    </div>
  );
}