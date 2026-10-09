# 维护与验证

Markdown 笔记是内容母稿；历史状态表记录学习计划，不是验收清单。修改概念时核对教材或官方资料，保留作者、引用和真实不确定性。

默认分支为 `feat/knowledge-network-enhancement`，保持现有分支，不将 main 的历史合并提交视为新的知识内容。

## 验证入口

```bash
npx --yes markdownlint-cli '**/*.md' --ignore node_modules --ignore .trunk --ignore .sisyphus
python3 scripts/check_readme.py
```

GitHub 的 Link Check 使用现有 `lychee.toml`。配置排除了大量学习中目录，其成功不能代表全仓链接均有效。上述离线检查核对 README 的真实相对文件链接、代码围栏与控制字符；代码块内路径仅作示例。

## 本次恢复

根目录逗号文件含独有 EC2 笔记，已原样移至 `cloud-devops/aws/ec2.md`，没有丢弃其内容。该笔记的若干相对链接目标尚未提供，内容中的价格和型号也未在本次重新核实；后续应逐条补齐来源与对应知识条目。三个仅含逗号和空格的根文件属于工具编辑残留，已删除。细节与原内容哈希见 `maintenance-evidence.json`。
