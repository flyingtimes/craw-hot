# Crawl Hot 变更日志

## [2026-02-28] v3.1 - 并发抓取优化

### 🚀 性能提升

**支持并发抓取多个用户**

### ✨ 新功能

- ✅ 支持并发抓取多个用户（默认 5 个并发）
- ✅ 添加浏览器操作锁，确保并发安全
- ✅ 显著提升抓取速度（特别是多用户场景）

### 🔧 配置选项

在 `Config` 类中新增：
```python
user_crawl_workers: int = 5  # 用户抓取并发数
```

### 🛠️ 技术实现

- 使用 `ThreadPoolExecutor` 实现并发抓取
- 使用 `threading.Lock` 保护浏览器操作
- 保持增量写入的文件安全特性
- 支持按完成顺序处理结果

### 📊 性能对比

- **之前**: 串行抓取，19 个用户约需 30-40 分钟
- **现在**: 5 并发抓取，19 个用户约需 8-10 分钟
- **提升**: 约 4 倍速度提升

### ⚠️ 注意事项

- 并发模式下，浏览器操作会加锁，确保不会冲突
- 单个用户抓取仍然使用浏览器锁保护
- 如需调整并发数，修改 `Config.user_crawl_workers` 配置

### 📝 使用方法

使用方法保持不变，自动启用并发：

```bash
# 抓取所有用户（自动使用 5 个并发）
python3 craw_hot.py crawl

# 抓取单个用户（串行）
python3 craw_hot.py crawl <username>
```

### 🔄 兼容性

- 完全向后兼容
- 不影响单个用户抓取
- 文件格式保持不变

---

## [2026-02-28] v3.0 - 架构重构

### 🎯 主要升级

**从单体架构迁移到模块化架构**

### ✨ 架构改进

#### 模块化设计
将原有的 650+ 行单体类拆分为 9 个独立模块，职责清晰：

- **Config** - 配置集中管理（使用 dataclass）
- **Logger** - 日志工具
- **ProcessLock** - 进程锁
- **BrowserClient** - 浏览器操作封装
- **TwitterApiClient** - Twitter API 客户端（fxtwitter + syndication）
- **PostFormatter** - 帖子内容格式化器
- **PostCrawler** - 帖子抓取器
- **UserManager** - 用户列表管理
- **ResultFileManager** - 结果文件管理
- **CrawlHot** - 主控制器（协调所有模块）

#### 代码质量提升
- ✅ 完整的类型提示
- ✅ DRY 原则（消除重复代码）
- ✅ 配置化（所有参数集中在 Config）
- ✅ 更清晰的代码结构
- ✅ 更易于测试和维护

### 📊 性能优化

- 保留原有的并发内容获取（10 个 worker）
- 智能滚动策略（连续 3 次无新帖则停止）
- 增量写入（每个用户抓取完立即保存）

### 🐛 Bug 修复

- 修复重构版缺失的 `os`、`sys`、`random` 模块导入

### 🔧 兼容性

- 完全向后兼容原有命令接口
- 保持相同的文件输出格式
- 保留所有原有功能特性

### 📝 使用方法

所有命令保持不变：

```bash
# 进入技能目录
cd /Users/clark/clawd/skills/craw-hot/scripts

# 添加用户
python3 craw_hot.py add <username>

# 删除用户
python3 craw_hot.py remove <username>

# 列出用户
python3 craw_hot.py list

# 抓取所有用户
python3 craw_hot.py crawl

# 抓取单个用户
python3 craw_hot.py crawl <username>
```

### 🔄 回滚

如果需要回滚到旧版本：

```bash
cd /Users/clark/clawd/skills/craw-hot/scripts
cp craw_hot_old.py craw_hot.py
```

### 📈 后续优化方向

- 添加单元测试
- 支持配置文件
- 添加更多 API 源
- 优化错误处理
- 支持自定义 Markdown 模板

---

## [之前版本]

### v2.4
- 进程锁机制
- 智能检测多实例

### v2.3
- 增量写入
- 实时进度显示

### v2.2
- 智能跳过（无新帖时不重试）

### v2.1
- 浏览器自动恢复

### v2.0
- 完整内容获取
- Markdown 导出
- 媒体支持
