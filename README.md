# Hitokoto 一言 自定义集成

为 Home Assistant 提供**一言**（Hitokoto）句子展示的传感器。支持任意兼容 `GET /api/random?category=xxx` 格式的 API 接口，默认使用 [hitokoto.cn](https://hitokoto.cn) 的官方 API。

## 功能特性

- 显示随机一言句子（`hitokoto` 字段）。
- 可配置 **API 基础 URL**，兼容任何符合 API 规范的第三方服务。
- 可选 **分类**（`category`），留空则不限制分类。
- 可自定义**更新间隔**（5分钟 ~ 1天）。
- 传感器额外属性包括：
  - `author`：作者
  - `categories`：所属分类列表
  - `commit_from`：提交来源
  - `created_at`：创建时间戳（Unix）
  - `length`：句子长度
  - `id`：句子唯一标识

## 安装方法

### 通过 HACS 安装（推荐）

1. 确保已安装 [HACS](https://hacs.xyz/)。
2. 将本仓库添加为自定义存储库：
   - 存储库地址：`https://github.com/Blear/hass-hitokoto`（请替换为实际地址）
   - 类别：**集成**
3. 在 HACS 中搜索 **“Hitokoto”** 并安装。
4. 重启 Home Assistant。

### 手动安装

1. 下载本仓库的 `custom_components/hitokoto` 文件夹。
2. 将其复制到 Home Assistant 的 `custom_components` 目录下（若无该目录则新建）。
3. 重启 Home Assistant。

## 配置

### 首次添加集成

1. 进入 **配置** → **设备与服务** → **添加集成**。
2. 搜索并选择 **“Hitokoto 一言”**。
3. 填写配置选项：

   | 选项 | 说明 | 示例 |
   |------|------|------|
   | **API 地址** | 必须为**基础 URL**（不含 `/api/random`），集成会自动拼接。 | `https://v1.hitokoto.cn` |
   | **分类** | 可选，指定分类名称（如 `励志`）。留空则随机返回任意分类。 | （留空）或 `励志` |
   | **更新间隔** | 多久请求一次 API，拉取新句子。 | `1 小时`（默认） |

4. 提交后，集成将自动创建传感器实体 `sensor.hitokoto_yi_yan`。

### 修改配置

- 进入集成列表，点击 **“Hitokoto 一言”** → **“配置”**。
- 修改任意选项并保存，集成会自动重载并应用新设置。

## 示例实体状态

**基础状态**（传感器值）：
```

生活不止眼前的苟且

````text
**额外属性**（`extra_state_attributes`）：
```json
{
  "author": "高晓松",
  "categories": ["励志", "经典"],
  "commit_from": "web",
  "created_at": 1744567890,
  "length": 10,
  "id": 42
}
````

## API 兼容性说明

集成期望 API 响应格式如下：

```json
{
  "id": 42,
  "hitokoto": "句子内容",
  "author": "作者",
  "categories": ["分类1", "分类2"],
  "commit_from": "web",
  "created_at": 1744567890,
  "length": 10
}
```

- 必须包含字段：`hitokoto`
- 其他字段缺失时，传感器属性中对应值为 `None`。

### 构建请求的 URL

- 完整请求 URL = `{API地址}/api/random?category={分类}`（若分类非空）
- 若分类为空，则不传递 `category` 参数。

**示例**：

- 输入 API 地址：`https://v1.hitokoto.cn`
- 分类：`励志`
- 实际请求：`https://v1.hitokoto.cn/api/random?category=励志`

## 升级注意事项

> **⚠️ 破坏性重构**
> 本版本（v2.0）**不兼容** v1.x 旧版配置。升级后需要删除并重新添加集成，或手动修改已失效的配置项（新增 `api_url`，分类由字母改为文字）。

### 从 v1.x 升级的步骤

1. 备份现有配置（可选）。
2. 删除旧的 Hitokoto 集成（在设备与服务中移除）。
3. 重启 Home Assistant。
4. 重新添加集成并按新要求填写配置。

## 故障排除

| 问题 | 可能原因 | 解决方法 |
| --- | --- | --- |
| 传感器显示 `未知` 或不可用 | API 地址错误、网络不通、API 返回格式不符 | 检查 `API 地址` 是否正确配置，确认能通过浏览器访问 `{API地址}/api/random` 获得正确 JSON |
| 属性中某些字段为 `None` | API 未返回该字段 | 这是正常的，日志中不会有错误，仅表示该次句子缺少该信息 |
| “加载失败”字样出现 | API 请求超时（10秒）或返回非 200 状态码 | 检查 API 服务是否稳定，必要时增加超时（需修改代码） |
| 更新间隔未生效 | 配置更改后集成未重载 | 可手动重载：进入集成 → 点击三个点 → “重新加载” |

## 开发者信息

- 代码仓库：[https://github.com/Blear/hass-hitokoto](https://github.com/Blear/hass-hitokoto)（请替换）
- 报告问题：[Issues](https://github.com/Blear/hass-hitokoto/issues)
- 贡献：欢迎提交 PR。

## 许可证

MIT License。详见 [LICENSE](https://LICENSE) 文件。

---
