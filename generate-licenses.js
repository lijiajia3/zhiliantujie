


const fs = require('fs');
const { execSync } = require('child_process');

function getLicenses() {
  console.log("📦 正在提取依赖包及其协议...");

  try {
    const output = execSync('npm list --all --json').toString();
    const json = JSON.parse(output);
    const flat = {};

    function flattenDeps(deps) {
      if (!deps) return;
      for (let [name, pkg] of Object.entries(deps)) {
        if (!flat[name]) {
          flat[name] = pkg.version;
          flattenDeps(pkg.dependencies);
        }
      }
    }

    flattenDeps(json.dependencies);

    const licenseInfo = [];
    for (let [pkg, version] of Object.entries(flat)) {
      try {
        const result = execSync(`npm view ${pkg}@${version} license`).toString().trim();
        licenseInfo.push({ name: pkg, version, license: result });
      } catch (err) {
        licenseInfo.push({ name: pkg, version, license: "未知" });
      }
    }

    fs.writeFileSync(
      './license-summary.json',
      JSON.stringify(licenseInfo, null, 2),
      'utf-8'
    );

    const markdown = licenseInfo
      .map(pkg => `| ${pkg.name} | ${pkg.version} | ${pkg.license} |`)
      .join('\n');

    fs.writeFileSync(
      './license-summary.md',
      `# 📜 项目依赖许可汇总\n\n| 包名 | 版本 | 协议 |\n|------|--------|--------|\n${markdown}`,
      'utf-8'
    );

    console.log("✅ 许可证信息已导出为 license-summary.json 和 license-summary.md");

  } catch (e) {
    console.error("❌ 提取失败：", e);
  }
}

getLicenses();