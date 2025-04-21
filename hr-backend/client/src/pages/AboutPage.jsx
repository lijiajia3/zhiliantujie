import React from "react";

export default function AboutPage() {
  return (
    <div style={{ padding: "40px", maxWidth: "800px", margin: "0 auto", fontFamily: "Arial, sans-serif" }}>
      <h1 style={{ fontSize: "28px", marginBottom: "20px" }}>关于我们</h1>
      <p style={{ fontSize: "16px", lineHeight: "1.8" }}>
        瑞佳恒创科技有限公司是一家专注于人力资源智能管理与数据驱动决策的科技型企业。我们致力于将前沿的大语言模型（LLM）与多模态知识图谱、智能数据治理相结合，为企事业单位提供一站式的人岗匹配与绩效优化解决方案。
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px" }}>
        公司产品“智链图解”系统广泛应用于第三产业与轻工业场景，通过自动简历分析、岗位推荐、绩效追踪与动态图表等模块，显著提升企业用工效率与管理精度。
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px" }}>
        我们的技术团队拥有丰富的机器学习、NLP、前后端开发与项目落地经验，已与多家事业单位建立合作，推动人力资源管理数字化升级。
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px" }}>
        本系统使用了多种符合 MIT、BSD、Apache 等开源许可协议的软件组件，包括但不限于 React、FastAPI、Chart.js、Axios 等。我们严格遵循各项开源协议的授权条款，已在系统中列出相关组件清单与许可证说明。项目中使用的所有第三方依赖仅用于系统构建与功能实现，未对原始代码进行封闭式二次发布或变更授权，确保符合商用合规要求。
      </p>
      <p style={{ fontSize: "16px", lineHeight: "1.8", marginTop: "16px" }}>
        若后续产品上线、商业化部署、对外合作或进行合规审计时，我们将持续维护依赖清单并保留相关许可证文本，确保避免任何版权争议。如对相关协议存在疑问，欢迎通过联系我们页面进行咨询。
      </p>
    </div>
  );
}
