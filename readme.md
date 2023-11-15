# Fake Data Generator

写一份 yaml，生成专属于你的假数据

本脚本仅够模拟数据，便于测试，以简化开发

## 环境

依赖于一些相当优秀的包：~~（因为觉得非常优秀所以内嵌引入了）~~

- faker（快速生成各种样式的假数据，并且支持 i18n ）
- xeger（反向 regex，通过正则表达式生成随机字符串）

```bash
pip install faker xeger
```

## 快速开始

克隆源码目录，然后将 `scheme.yaml` 复制一份并重命名，然后执行命令：

```bash
python main.py your-scheme.yaml
```

## 使用前提醒

该脚本所能生成的数据结构类似于大多数的 SQL 数据库，数据中包含多个表（table），每个表包含若干个字段（field）

所以该脚本主要针对的需求是生成数据库的随机数据并方便项目测试（目前无计划实现 mock 数据库服务器且已经有更好的选择），并且脚本内计划/已经添加了多个支持“数据间关系”甚至“数据表之间关系”的特性，可以在中等偏大型的数据库中也可一用

如数据需放在 excel 中进行展示，也较为好用，但暂未支持直接生成 excel 文件，可以先生成 csv 并导入至 excel

## TODO

- 更多语境函数
- 支持每个表使用不同的生成数量
- 支持导出到 sql 语句
- 支持导出到 excel 文件

## Schema 结构

可以查看这个简单的[示例](./schema.yaml)

schema 共分为4个部分：

|名称|作用|是否必须|
|---|---|---|
|faker|配置 faker 相关参数|必须|
|params|配置生成器的相关参数|必须|
|env|用户自定义变量|可选|
|struct|数据表结构|必须|

### faker

目前支持配置 faker 的语言以及 faker 内部预提供的 provider，也支持用户自定义 provider

其格式大致如下：

```yaml
faker:
  # 配置 faker 生成随机数据时允许使用的语言（默认英语）
  locales:
    - zh_CN
    - zh_TW
  # 配置 faker 的 provider
  providers:
    # faker 内置的 provider
    - internet
    - address
    # 用户自定义的 provider
    - name: my_provider
      source: my_provider.txt # 词条之间需要用常见分隔符分隔，如空格、英文逗号、英文分号、换行符、竖线等
```

### params

这里控制生成数据的条数以及数据的格式

```yaml
params:
  # 生成数据的数量（目前每个表统一都会生成这么多）
  amount: 100
  # 生成数据的格式，目前支持 csv、print
  format: csv
  # 对应不同的生成格式，有不同的参数可以选，这里是 csv 对应的参数示例
  args:
    separator: '|'
```

### env

如果想要自己添加一些数据或者是常量，并且在生成过程中使用的话，这个部分就是为这个功能而准备的

```yaml
env:
  hello: yes!
  fake:
    date: 288
```

在 `eval` 生成器（具体用法见下文）下，使用方式为：

```python
env.hello      # "yes!"
env.fake.date  # 288
```

### struct

这里是最重要的部分之一，控制着脚本生成什么样的数据

基本结构如下：

```yaml
struct:
  table_name_1:
    field_name_1:
      if:     # 生成条件（非必须，具体见后文的条件生成介绍）
      rule:   # 生成规则（缺省则生成器为 const）
      value:  # 生成器字面量（除 none 生成器外，必须）
      type:   # 强制转换类型（非必须）
      args:   # 生成器参数（非必须）
    field_name_2:
      ...
  table_name_2:
    ...
```

目前仅允许使用内置的生成器

下面介绍每个生成器的用法

#### const

最基本的生成器，直接将 `value` 放到最终数据里

如果 `rule` 不写的话会默认地使用 `const` 生成器

```yaml
rule: const
value: Hello Fake Data
# 示例生成：'Hello Fake Data'
```

#### range

根据范围生成随机数字，可选整数或小数

```yaml
rule: range
value: 1...100
# 生成 [1, 100] 区间内的随机数（注意两端都包含）

rule: range
value: 1.0...100.0
# 只要有一个数是小数的话，会启用小数生成模式
# 生成 [1.0, 100.0) 之间的随机小数
```

#### increase/decrease

自增/自减生成器，由于比较相似所以直接放在一起介绍

从 `value` 指定的值开始（包括它自身），每新的一行自加一/减一

```yaml
rule: increase
value: 2
# 输出：2
# 下一个输出：3
# 下一个输出：4
# ...
```

#### enum

根据给定的一些值，随机选取其中的一个

这个生成器在构造枚举值的时候较为好用

```yaml
rule: enum
value:
  - 男
  - 女
  - 保密
# 输出是随机选取“男”、“女”、“随机”中的一个
```

#### regex

借助 `xeger` 实现用正则表达式生成随机的字符串

```yaml
rule: regex
value: [a-zA-Z]{3}
# 输出示例：'aUx'
```

#### eval

非常灵活的生成器，`value` 字符串会被视作一段 python 语句，生成的结果将作为最终数据的值

`value` 处可以直接引用全局语境下的变量（详见后文介绍全局语境），例如 `fake`、`xeger`、`line` 等（对于 xeger 对象，非特殊需求下，直接使用 regex 生成器似乎更简洁一点）

也可以使用自定义的 `env` 对象，并且无需像字典一样使用，`env` 会自动包装成一个对象，用点运算符取成员即可

```yaml
# 使用 faker 对象
value: fake.name()
# 输出示例：'李华'

# 作为 python 语句执行
value: fake.name() + '先生'
# 输出示例：'李华先生'

# 使用 xeger 对象
value: xeger('\d{4}')
# 输出示例：'3784'

# 使用 env 对象
value: env.hello + 'foo'
# 输出示例（这里的 env 取上文的 env 示例）：'yes!foo'
```

#### foreign

目前为止最为复杂的生成器

TODO

#### none

生成的数据是啥也没有（也就是 python 中的 `None`）

在数据里一般会留空，若指定了 `type` 为 `str` 则会变成一个空字符串

none 生成器不需要指定 `value` 也可以工作

```yaml
rule: none
# 输出：（这里什么也没有）
```

## 全局语境 context

在生成脚本的时候，某些地方会被视作 python 语句，使用 `eval()` 函数计算其实际值，为了使脚本更加方便，eval 时会传入一个语境对象，包含了许多有用的变量可以调用

|变量名|类型|说明|
|---|---|---|
|env|object|用户自定义的变量|
|fake|Faker object|预生成的 Faker 对象|
|xeger|function|Xeger 对象中的一个成员函数|
|line|object|存有当前行的数据对象|

### line 对象的限制

由于脚本是按列生成数据的，并且位置靠前的列会优先被生成，并且 line 对象所能够引用的只有已经生成的列的数据，而有时候靠前的数据列也需要依据靠后的列进行条件判断等，此时可以在生成器声明中加上 `order` 选项

所有生成器的默认 `order` 均为`0`，若 `order` 有不同，则 `order` 更小的列优先生成，且相同 `order` 的列会由前到后依次生成

例如：若需要某一列最先生成，可以将 `order` 设为`-1`

**要注意的是**，order 的大小不影响最终呈现在数据表中的顺序，最终呈现的顺序永远是依照 schema 中书写的由上到下的顺序，order 只能决定每一列生成的顺序

## 字段生成条件

对于每一个字段，默认支持了多个生成器，只需要用列表的方式写出每个生成器即可

if 选项内的字符串也会被视作 python 语句，并且也可以调用全局语境内的任意变量

```yaml
field_name:
  # 使用正则表达式随机生成一个数字，并且如果大于等于5则使用第一个生成器
  - if: xeger('\d') >= 5
    rule: const
    value: 男
  # 若上一个生成器的条件不满足，则顺延至后一个生成器
  - rule: const
    value: 女
```

每一个生成器都可以配置一个 if 选项，某一个生成器不生效时则会顺延至下一个生成器，若该字段已声明的所有生成器都不生效时，脚本会采用一个隐式的 none 生成器，即不生成任何内容

另一个常见用途是根据当前数据行的某一个字段，判断另一个字段应该生成什么样的数据（引用 line 对象时注意其特殊性：只能引用到已经生成的列）

```yaml
# 这里的 schema 仅举例，比较牵强，实际使用中可能会有更好的例子
is_adult:
  rule: enum
  value:
    - 0
    - 1
age:
  # 如果是成年人则年龄应生成18~30之间
  - if: line.is_adult == 1
    rule: range
    value: 18...30
  # 否则生成小于18岁的随机年龄
  - rule: range
    value: 12...17
```

善用 if 选项可以让假数据也有一定的逻辑性，但在实际工程中是否应该使用则见仁见智

- 逻辑错误的假数据也能够一定程度上反应某些系统对错误处理的能力
- 如果系统的输入中已经有了完善的逻辑检查（即保证了数据库中的数据理一定是符合逻辑的），此时使用 if 选项可以避免不必要的逻辑错误
