# Ansible (自动化配置管理)

## 简介

Ansible 是 Red Hat 开发的开源自动化工具，用于软件配置、应用部署和基础设施编排。它采用无代理架构（Agentless），通过 SSH 连接管理节点，使用 YAML 编写的 Playbook 描述期望状态，简洁易读且功能强大。

## 核心概念

### 1. Inventory
- **主机清单**: 定义被管理节点的列表
- **分组**: 按功能、环境对主机分组（webservers、dbservers）
- **变量**: 为主机或组定义变量
- **动态 Inventory**: 从云平台 API 动态获取主机列表

### 2. Playbook
- **剧本**: YAML 格式的自动化任务编排文件
- **Play**: 针对一组主机执行的任务集合
- **Task**: 单个原子操作，调用模块完成具体工作
- **Handler**: 事件驱动的任务，仅在被通知时执行

### 3. Modules
- **核心模块**: file、copy、template、service、package 等
- **云模块**: AWS、Azure、GCP、Docker、K8s 集成
- **自定义模块**: 使用 Python 编写扩展功能
- **幂等性**: 多次执行结果一致

### 4. Roles
- **角色**: 可复用的 Playbook 组织结构
- **标准化目录**: tasks、handlers、templates、files、vars、defaults
- **依赖管理**: 角色可以依赖其他角色
- **Galaxy**: Ansible Galaxy 共享和下载角色

### 5. Variables
- **优先级**: 命令行 > Playbook > Inventory > Role defaults
- **Facts**: 自动收集的系统信息（IP、OS、内存等）
- **魔法变量**: hostvars、group_names、inventory_hostname 等
- **Vault**: 加密敏感变量

## 实现方式

### Inventory 配置

```ini
# inventory/hosts.ini
# 基础主机定义
[webservers]
web1.example.com ansible_host=192.168.1.10
web2.example.com ansible_host=192.168.1.11 ansible_user=ubuntu

[dbservers]
db1.example.com ansible_host=192.168.1.20

# 分组变量
[webservers:vars]
ansible_user=deploy
ansible_ssh_private_key_file=~/.ssh/web_key
http_port=80

[dbservers:vars]
ansible_user=dbadmin
ansible_ssh_private_key_file=~/.ssh/db_key

# 嵌套分组
[servers:children]
webservers
dbservers

# 主机变量（推荐在 host_vars/ 目录中定义）
```

```yaml
# inventory/group_vars/all.yml
---
# 全局变量
ntp_servers:
  - 0.pool.ntp.org
  - 1.pool.ntp.org

dns_servers:
  - 8.8.8.8
  - 8.8.4.4

# 加密变量（使用 ansible-vault 加密）
vault_database_password: !vault |
  $ANSIBLE_VAULT;1.1;AES256
  ...

# inventory/group_vars/webservers.yml
---
# Web 服务器组变量
app_name: myapp
app_version: "2.1.0"
app_port: 8080

nginx_worker_processes: auto
nginx_worker_connections: 4096
```

### Playbook 编写

```yaml
# site.yml - 主 Playbook
---
- name: Configure all servers
  hosts: all
  become: yes
  gather_facts: yes

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600
      when: ansible_os_family == "Debian"

  roles:
    - common
    - monitoring

- name: Configure web servers
  hosts: webservers
  become: yes

  vars:
    app_environment: production

  roles:
    - nginx
    - nodejs
    - app_deploy

  post_tasks:
    - name: Verify web service
      uri:
        url: "http://localhost:{{ app_port }}/health"
        status_code: 200
      register: health_check
      retries: 5
      delay: 10
      until: health_check.status == 200

- name: Configure database servers
  hosts: dbservers
  become: yes

  roles:
    - mysql
    - mysql_backup
```

### 详细任务示例

```yaml
# roles/nginx/tasks/main.yml
---
- name: Install Nginx
  package:
    name: nginx
    state: present
  notify: restart nginx

- name: Create document root
  file:
    path: "/var/www/{{ app_name }}"
    state: directory
    owner: www-data
    group: www-data
    mode: '0755'

- name: Deploy Nginx configuration
  template:
    src: nginx.conf.j2
    dest: /etc/nginx/nginx.conf
    owner: root
    group: root
    mode: '0644'
    validate: 'nginx -t -c %s'
  notify: reload nginx

- name: Deploy site configuration
  template:
    src: site.conf.j2
    dest: "/etc/nginx/sites-available/{{ app_name }}"
    owner: root
    group: root
    mode: '0644'
  notify: reload nginx

- name: Enable site
  file:
    src: "/etc/nginx/sites-available/{{ app_name }}"
    dest: "/etc/nginx/sites-enabled/{{ app_name }}"
    state: link
  notify: reload nginx

- name: Remove default site
  file:
    path: /etc/nginx/sites-enabled/default
    state: absent
  notify: reload nginx

- name: Deploy application files
  copy:
    src: "{{ item }}"
    dest: "/var/www/{{ app_name }}/"
    owner: www-data
    group: www-data
    mode: '0644'
  loop:
    - index.html
    - styles.css
  notify: reload nginx

# Handler 定义
# roles/nginx/handlers/main.yml
---
- name: restart nginx
  service:
    name: nginx
    state: restarted

- name: reload nginx
  service:
    name: nginx
    state: reloaded
```

### Jinja2 模板

```jinja2
{# roles/nginx/templates/site.conf.j2 #}
server {
    listen {{ nginx_listen_port | default(80) }};
    server_name {{ inventory_hostname }};

    root /var/www/{{ app_name }};
    index index.html index.htm;

    {% if app_environment == 'production' %}
    # Production optimizations
    gzip on;
    gzip_types text/plain text/css application/json;
    {% endif %}

    location / {
        try_files $uri $uri/ =404;
    }

    {% for location in nginx_locations | default([]) %}
    location {{ location.path }} {
        proxy_pass {{ location.proxy_pass }};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    {% endfor %}

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### Python 动态 Inventory

```python
#!/usr/bin/env python3
"""AWS EC2 动态 Inventory 脚本"""
import json
import boto3
from argparse import ArgumentParser

class EC2Inventory:
    def __init__(self):
        self.ec2 = boto3.client('ec2')
    
    def get_inventory(self):
        """获取 EC2 实例并生成 Inventory"""
        inventory = {
            '_meta': {'hostvars': {}},
            'all': {'children': []},
            'ungrouped': {'hosts': []}
        }
        
        # 获取所有运行中的实例
        response = self.ec2.describe_instances(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]
        )
        
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                host = instance.get('PublicDnsName') or instance['PrivateIpAddress']
                instance_id = instance['InstanceId']
                
                # 提取标签
                tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                environment = tags.get('Environment', 'ungrouped')
                role = tags.get('Role', 'unknown')
                
                # 创建分组
                group_name = f"{environment}_{role}"
                if group_name not in inventory:
                    inventory[group_name] = {'hosts': []}
                
                inventory[group_name]['hosts'].append(host)
                
                # 主机变量
                inventory['_meta']['hostvars'][host] = {
                    'ansible_host': instance['PrivateIpAddress'],
                    'instance_id': instance_id,
                    'instance_type': instance['InstanceType'],
                    'availability_zone': instance['Placement']['AvailabilityZone'],
                    'environment': environment,
                    'role': role
                }
        
        # 添加分组层级
        for group in list(inventory.keys()):
            if not group.startswith('_') and group not in ['all', 'ungrouped']:
                parts = group.split('_')
                if len(parts) == 2:
                    env, role = parts
                    # 环境组
                    if env not in inventory:
                        inventory[env] = {'children': []}
                    if 'children' not in inventory[env]:
                        inventory[env]['children'] = []
                    inventory[env]['children'].append(group)
                    
                    # 角色组
                    if role not in inventory:
                        inventory[role] = {'children': []}
                    if 'children' not in inventory[role]:
                        inventory[role]['children'] = []
                    inventory[role]['children'].append(group)
        
        return inventory
    
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}

def main():
    parser = ArgumentParser()
    parser.add_argument('--list', action='store_true', help='List all hosts')
    parser.add_argument('--host', help='Get host variables')
    args = parser.parse_args()
    
    inventory = EC2Inventory()
    
    if args.list:
        print(json.dumps(inventory.get_inventory(), indent=2))
    elif args.host:
        print(json.dumps(inventory.empty_inventory()))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
```

### Ansible Vault 使用

```bash
#!/bin/bash
# Ansible Vault 管理脚本

VAULT_FILE="group_vars/all/vault.yml"
VAULT_PASSWORD_FILE=".vault_pass"  # 确保在 .gitignore 中

# 创建加密文件
vault_create() {
    ansible-vault create "$VAULT_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 编辑加密文件
vault_edit() {
    ansible-vault edit "$VAULT_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 加密现有文件
vault_encrypt() {
    ansible-vault encrypt "$1" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 解密文件
vault_decrypt() {
    ansible-vault decrypt "$VAULT_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 查看加密文件内容
vault_view() {
    ansible-vault view "$VAULT_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 重新加密（更换密码）
vault_rekey() {
    ansible-vault rekey "$VAULT_FILE" --vault-password-file "$VAULT_PASSWORD_FILE"
}

# 运行 Playbook（自动使用 vault 密码）
run_playbook() {
    ansible-playbook site.yml --vault-password-file "$VAULT_PASSWORD_FILE" "$@"
}

# 生成随机 vault 密码
generate_password() {
    openssl rand -base64 32 > "$VAULT_PASSWORD_FILE"
    chmod 600 "$VAULT_PASSWORD_FILE"
    echo "Vault password generated in $VAULT_PASSWORD_FILE"
}

case "$1" in
    create) vault_create ;;
    edit) vault_edit ;;
    encrypt) vault_encrypt "$2" ;;
    decrypt) vault_decrypt ;;
    view) vault_view ;;
    rekey) vault_rekey ;;
    run) shift; run_playbook "$@" ;;
    gen-pass) generate_password ;;
    *) echo "Usage: $0 {create|edit|encrypt|decrypt|view|rekey|run|gen-pass}" ;;
esac
```

### 条件执行和循环

```yaml
# 条件执行任务
- name: Install Apache (Debian/Ubuntu)
  apt:
    name: apache2
    state: present
  when: ansible_os_family == "Debian"

- name: Install HTTPD (RHEL/CentOS)
  yum:
    name: httpd
    state: present
  when: ansible_os_family == "RedHat"

# 复杂条件
- name: Configure production settings
  template:
    src: production.yml.j2
    dest: /etc/app/config.yml
  when:
    - app_environment == "production"
    - ansible_memtotal_mb >= 4096
    - app_version is version('2.0', '>=')

# 循环
- name: Create users
  user:
    name: "{{ item.name }}"
    state: present
    groups: "{{ item.groups | default(omit) }}"
    shell: "{{ item.shell | default('/bin/bash') }}"
  loop:
    - { name: 'alice', groups: 'developers,sudo' }
    - { name: 'bob', groups: 'developers' }
    - { name: 'charlie', shell: '/bin/zsh' }

# 字典循环
- name: Configure environment variables
  lineinfile:
    path: /etc/environment
    line: "{{ item.key }}={{ item.value }}"
  loop: "{{ env_vars | dict2items }}"
  vars:
    env_vars:
      JAVA_HOME: /usr/lib/jvm/java-11
      NODE_ENV: production
      API_ENDPOINT: https://api.example.com

# 文件列表循环
- name: Ensure directories exist
  file:
    path: "{{ item }}"
    state: directory
    mode: '0755'
  loop:
    - /var/log/myapp
    - /var/lib/myapp
    - /etc/myapp/conf.d
```

## 示例

### 完整 Role 结构

```
roles/
└── app_deploy/
    ├── defaults/
    │   └── main.yml        # 默认变量（优先级最低）
    ├── vars/
    │   └── main.yml        # 角色变量
    ├── tasks/
    │   ├── main.yml        # 入口任务
    │   ├── install.yml     # 安装任务
    │   └── configure.yml   # 配置任务
    ├── handlers/
    │   └── main.yml        # 事件处理器
    ├── templates/
    │   ├── app.service.j2  # systemd 服务模板
    │   └── config.yml.j2   # 应用配置模板
    ├── files/
    │   └── binary.tar.gz   # 静态文件
    └── meta/
        └── main.yml        # 角色元数据（依赖）
```

### Ad-hoc 命令

```bash
# Ping 所有主机
ansible all -i inventory/hosts.ini -m ping

# 执行命令
ansible webservers -a "uptime"
ansible webservers -m shell -a "df -h | grep /dev/sda"

# 批量安装软件
ansible all -m apt -a "name=htop state=present" --become

# 复制文件
ansible webservers -m copy -a "src=./app.conf dest=/etc/app/ mode=0644" --become

# 使用变量
ansible webservers -m template -a "src=nginx.conf.j2 dest=/etc/nginx/nginx.conf" \
  -e "worker_processes=4" --become

# 滚动执行（一次一台）
ansible webservers -a "reboot" -f 1 --become
```

## 应用场景

1. **服务器初始化**: 自动化系统配置、用户管理、安全加固
2. **应用部署**: CI/CD 流程中的应用发布和回滚
3. **配置管理**: 确保服务器配置一致性和合规性
4. **编排协调**: 多节点服务的协调部署
5. **灾难恢复**: 快速重建基础设施和应用环境

## 面试要点

Q: Ansible 与 Puppet/Chef 的主要区别是什么？
A: 核心区别：
   - **架构**: Ansible 是无代理（SSH），Puppet/Chef 需要安装 Agent
   - **语言**: Ansible 使用 YAML，更简洁；Puppet 使用 DSL，Chef 使用 Ruby
   - **执行**: Ansible 是推模式（Push），Puppet 是拉模式（Pull）
   - **幂等性**: 三者都支持，但 Ansible 更简单直观
   - **适用场景**: Ansible 适合临时任务和快速部署，Puppet/Chef 适合大规模持续管理

Q: 如何实现 Ansible 的幂等性？
A: 幂等性保证：
   - 使用状态模块（state=present/absent）而非命令模块
   - 利用内置模块（file、copy、template、service）而非 shell/command
   - Handler 只在状态变更时触发
   - 使用条件判断（when、changed_when）控制执行
   - 避免使用 `shell` 和 `command` 模块执行有副作用的操作

Q: Ansible 变量优先级是怎样的？
A: 从高到低：
   - 命令行 `-e` 传入的变量
   - Task 级别的 `vars`
   - Block 级别的 `vars`
   - Play 级别的 `vars`
   - 主机变量 `host_vars/`
   - 组变量 `group_vars/`
   - Role 的 `vars/main.yml`
   - Role 的 `defaults/main.yml`

Q: 如何处理 Ansible 中的敏感数据？
A: 安全措施：
   - 使用 Ansible Vault 加密敏感变量文件
   - 使用 `no_log: true` 隐藏敏感任务的输出
   - 集成外部密钥管理系统（HashiCorp Vault、AWS Secrets Manager）
   - 通过环境变量传递敏感信息
   - 限制日志文件权限，避免敏感信息泄露

Q: Ansible 动态 Inventory 的使用场景是什么？
A: 适用场景：
   - 云环境（AWS EC2、Azure VM、GCP）主机动态变化
   - 容器编排平台（Kubernetes、Docker Swarm）
   - 自动扩缩容场景下的主机发现
   - CMDB 系统集成，从数据库获取主机信息
   - 减少静态维护 Inventory 的工作量，实现真正的基础设施即代码


## 相关概念

### 数据结构
- **YAML 树结构**：Playbook 使用嵌套的键值对和列表表示配置
- **Inventory 分组**：支持多层级主机分组和变量继承

### 算法
- **并行执行策略**：默认并行（forks=5），通过 `serial` 控制批次
- **幂等性检查**：模块内部比较期望状态与实际状态

### 复杂度分析
| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| Inventory 解析 | O(n) | n=主机数量 |
| 任务执行 | O(m × n) | m=任务数，n=主机数 |
| Handler 触发 | O(k) | k=触发次数（去重后） |

### 系统实现
- **SSH 通信**：基于 Paramiko 或 OpenSSH 的传输层
- **Facts 收集**：使用 `setup` 模块收集主机信息（JSON 格式）
- **回调插件**：支持自定义执行结果处理（日志、通知等）

### 关联文件
- [Docker](./docker.md) - Ansible 可自动化 Docker 部署
- [Kubernetes](./kubernetes/kubectl.md) - 使用 Ansible 管理 K8s 资源
- [分布式系统](../distributed-systems/README.md) - 大规模集群配置管理
- [安全](../security/authentication.md) - 安全基线配置与合规检查

