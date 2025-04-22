const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
const User = require("./models/User");

const app = express();
const PORT = 4000;

// 中间件
app.use(cors());
app.use(express.json());

// ✅ 连接 MongoDB 数据库
mongoose.connect("mongodb://127.0.0.1:27017/hr", {
  useNewUrlParser: true,
  useUnifiedTopology: true,
}).then(() => {
  console.log("✅ MongoDB 已连接");
}).catch((err) => {
  console.error("❌ MongoDB 连接失败", err);
});

// ✅ 模拟员工接口
const employees = [
  {
    id: 1,
    name: "张三",
    gender: "男",
    education: "本科",
    experience: 3,
    skills: ["Excel", "沟通", "设备维护"],
    certificates: ["中级技工"],
    performance: 87,
    satisfaction: 80
  },
  {
    id: 2,
    name: "李四",
    gender: "女",
    education: "专科",
    experience: 5,
    skills: ["维修", "管理"],
    certificates: ["高级维修工"],
    performance: 92,
    satisfaction: 85
  }
];

app.get("/employees", (req, res) => {
  console.log("📥 收到一个 /employees 请求！");
  res.json(employees);
});

// ✅ 登录接口（调试中）
app.post("/login", async (req, res) => {
  const { identifier, password } = req.body;
  console.log("📥 收到登录请求：", identifier, password);

  try {
    console.log("🧾 正在查询 username 为 testuser");
    // 暂时写死测试用户
    const user = await User.findOne({ username: "testuser" });
    console.log("🔍 查询结果：", user);

    if (!user) {
      console.log("❌ 用户不存在");
      return res.status(401).json({ status: "fail", message: "用户不存在" });
    }

    if (user.password === password) {
      console.log("🎉 密码正确，登录成功");
      return res.json({
        status: "success",
        role: user.role,
        token: "mock-token"
      });
    } else {
      console.log("❌ 密码错误");
      return res.status(401).json({ status: "fail", message: "密码错误" });
    }
  } catch (err) {
    console.error("❌ 登录出错", err);
    return res.status(500).json({ status: "error", message: "服务器错误" });
  }
});

// ✅ 启动服务
app.listen(PORT, "0.0.0.0", () => {
  console.log(`✅ Server is running on http://localhost:${PORT}`);
});
app.get("/profile", (req, res) => {
  const authHeader = req.headers.authorization;
  console.log("🔐 收到 profile 请求，Header 为：", authHeader);

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ message: "未授权访问" });
  }

  const token = authHeader.split(" ")[1];

  if (token !== "mock-token") {
    return res.status(401).json({ message: "无效 token" });
  }

  return res.json({
    username: "testuser",
    role: "admin",
  });
});
app.get("/profile", (req, res) => {
  const authHeader = req.headers.authorization;
  if (!authHeader) return res.status(401).json({ message: "未授權" });

  const token = authHeader.split(" ")[1];
  if (token === "mock-token") {
    return res.json({ username: "testuser", role: "admin" });
  } else {
    return res.status(401).json({ message: "無效 token" });
  }
});
