# Fake Data Generator

> 只写一份 yaml，生成专属于你的假数据（

## 环境

依赖于一些相当优秀的包：~~（因为觉得非常优秀所以内嵌引入了）~~

- faker（快速生成各种样式的假数据，并且支持 i18n ）
- xeger（反向 regex，通过正则表达式生成随机字符串）

```bash
pip install faker xeger
```

## 前置知识

使用这个脚本需要了解 yaml 的基本格式，以及少量的 python 语法

## 快速开始

克隆源码目录，然后将 `scheme.yaml` 复制一份并重命名，然后执行命令：

```bash
python main.py your-scheme.yaml
```

## 使用前提醒

该脚本所能生成的数据结构类似于大多数的 SQL 数据库，数据中包含多个表（table），每个表包含若干个字段（field）

所以该脚本主要针对的需求是生成数据库的随机数据并方便项目测试（目前无计划实现 mock 数据库服务器且已经有更好的选择），并且脚本内计划/已经添加了多个支持“数据间关系”甚至“数据表之间关系”的特性，在中等偏大型的数据库中也可一用

如数据需放在 excel 中进行展示，也较为好用，但暂未支持直接生成 excel 文件，可以先生成 csv 并导入至 excel

## TODO

- 更多语境函数
- 支持每个表使用不同的生成数量
- 支持导出到 sql 语句
- 支持导出到 excel 文件

## Schema 结构

可以查看这个简单的[示例](./sample_schema.yaml)

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

你可以在 faker 的[文档](https://faker.readthedocs.io/en/master/locales.html)处找到可用的语言以及对应的 providers

### params

这里控制生成数据的条数以及数据的格式，目前自定义程度较低，仍需完善

```yaml
params:
  # 生成数据的数量（此处不填的话默认为10）
  amount: 30
  # 生成数据的格式，目前支持 print、csv、sql
  format: csv
  # 对应不同的生成格式，有不同的参数可以选，这里是 csv 对应的参数示例
  args:
    separator: '|'
    headers: true
```

#### print 模式

该模式直接在控制台输出一串数组（`python list`）

#### 生成 csv

生成 csv 可选的参数目前如下：

|参数|说明|
|---|---|
|separator|分割符，默认为 `,`|
|headers|是否添加表头，默认为 `false` 不添加|

#### 生成 sql

目前功能略微欠缺，仅支持生成形如 `INSERT INTO ... (...) VALUES (...);` 的语句，且不支持参数

### env

如果想要自己添加一些数据或者是常量，并且在生成过程中使用的话，这个部分就是为这个功能而准备的

```yaml
env:
  hello: yes!
  fake:
    date: 288
```

这个 env 会被自动包装成一个 python 对象，调用方式大致如下：

```python
env.hello      # "yes!"
env.fake.date  # 288
```

### struct

这里是最重要的部分之一，控制着脚本生成什么样的数据

其基本结构是：struct 下是多个表名，每个表名下是它对应的字段名，然后每个字段下的对象是一个生成器对象，如果字段下是一个列表的话，那么视为使用了多个生成器，列表中的每一项都应符合生成器的声明格式

示例如下：

```yaml
struct:
  table_name_1:
    field_name_1:
      if: random.random() > 0.5
      order: -1
      unique: True
      rule: eval
      value: fake.name()
      type: str
      args: null
    field_name_2:
      ...
  table_name_2:
    ...
```

可见生成器是生成数据时最主要的对象之一，其声明如下

|选项|说明|是否必须|
|---|---|---|
|rule|生成器规则，每个规则对应了一种生成器|必须，不写默认为 `const`|
|value|生成器传入的值，用于规定生成数据的格式|除 `none` 生成器外，必须|
|type|将结果强制类型转换|可选 `str`, `int`, `float`，不填则不转换（保留生成器的结果类型）|
|if|控制该生成器是否运行|可选，默认为 `True`|
|order|控制该字段的生成优先级，值越小优先级越高|可选，默认为`0`，多个生成器会选取最大的 order|
|unique|控制生成的内容是否不可重复|可选，默认为`False`|
|limit|用于约束生成的结果，使最终结果必然符合表达式或为 `None`|可选，默认为`True`|
|args|某些生成器可能需要额外的参数以工作|可选|

要注意的是，这些生成器会被逐个构建、调用，并且**按列**生成数据，最终生成的数据，列的顺序将会按照 schema 由上到下的顺序排列（指定 order 不会影响最终的排列顺序）

由于脚本没有强大到能够分析出你的生成器会产生多少值，在某些情况下（特别是声明了 unique 的情况下），生成器没有办法再生成满足条件的值（这在脚本中被称为“碰撞”，即 `Collide`），生成器会尝试足够多次，多次依旧无法生成时则会生成 `None`

典型的例子是，你需要生成100组数据，但某个字段使用了 range 生成 1~99 的随机数，并且指定了 unique 选项。此时该字段由于最多只能产生99种不同的可能，对于生成100组数据并且不重复的要求，显然是无法实现的，此时就会产生上述的“碰撞”，最后一行该字段理应会成为 `None` 并留空

发生上述碰撞时，会在控制台的最终结果中显示生成失败（即 `Failed`）的次数，注意：发生碰撞不一定意味着生成失败，也有可能是 unique 字段搭配随机数时，出现了重复的值，在尝试多次（即碰撞多次）后成功生成了，只有在尝试足够多次后依旧没有成功生成才会被判定为失败

目前脚本中的“足够多次”暂定为100次，后续可能会动态调整，或者让用户进行定义

> 其实大致有办法能检查出来并及时报错，但对于每个生成器都会有不同的检查方式，也是一件麻烦事，并且检查出来之后也很难自动的修复或者使用某种默认值，最多只能提醒用户更改，相比之下由用户自己保证可行性效率反而更高

目前仅允许使用内置的生成器，下面介绍每个生成器的用法

#### const

最基本的生成器，直接将 `value` 作为最终数据

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
# 输出是随机选取“男”、“女”、“保密”中的一个
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

# 使用 xeger 函数
value: xeger('\d{4}')
# 输出示例：'3784'

# 使用 env 对象
value: env.hello + 'foo'
# 输出示例（这里的 env 取上文的 env 示例）：'yes!foo'
```

#### foreign

目前为止最为复杂的生成器，能够引用到其它表中的数据（这里非常类似于 SQL 中的外键）

其 value 选项的格式形如 `表名.字段名`，这会告诉生成器你需要对应到哪一个字段，并且由于这种“对应”比较模糊，foreign 生成器还需要指定 args 才能正常工作

args 中最主要的参数是 cast，该选项决定了生成器怎样从目标字段映射到本字段

cast 支持3种模式：

- one

一一对应模式，例如唯一存在的 id，能够保证本字段的每一个值，都能对应到目标字段的某一个值，且不会发生重复，即本字段的数据集合和目标字段的集合完全等价

- random

随机映射模式，能够保证本字段的值都来自于目标字段，但有可能发生重复，即本字段的数据集合是目标字段的子集

- filter

筛选模式，该模式需要指定额外的 filters 参数

filters 可以是一个 filter 对象，也可以是多个 filter 对象组成的列表，每个 filter 对象包含两个值：field 和 condition

filter 的作用是筛选目标表的行 ~~（好抽象啊）~~，下面是一个例子

```yaml
# 这个表结构比较冗余，但却是一个很好的例子
# 它声明的两个表中，有两个完全相同且要求数据也相同的字段
struct:
  table_a:
    id:
      rule: increase
      value: 0
    name:
      rule: eval
      value: fake.name()
  table_b:
    # 外键指向 table_a 中的 id 字段，并且能够一一对应
    id:
      rule: foreign
      value: table_a.id
      args:
        cast: one
    # 指向 table_a 的 name 字段
    name:
      rule: foreign
      value: table_a.name
      args:
        # 声明使用筛选模式
        cast: filter
        filters:
          # 筛选器需要筛选 table_a 中的 id 字段
          field: id
          # 筛选条件为：目标行的 id == 本行的 id
          # condition 中自带的 field 变量会被替换成：目标表.field
          condition: field == line.id
          # 由于 table_b 的 id 字段会与 table_a 的 id 一一对应
          # 所以经过这个筛选器筛选之后，有且仅有一条数据能被筛选出来
          # 所以在两个表中的 id 和 name 全部都是一一对应的，且对应关系不会出错
```

如果觉得过于复杂，可以将这个表结构自己动手生成一下看看最终的效果

> foreign 生成器虽然复杂（特别是 filter 模式），但在某些情况下还是非常好用的，~~熟悉之后你会喜欢上它的~~

#### none

不生成任何东西（也就是 python 中的 `None`）

在数据里一般会留空，若指定了 `type` 为 `str` 则会变成字符串 `'None'`

none 生成器不需要指定 `value` 也可以工作

```yaml
rule: none
# 输出：
#（就是空白，这里什么也没有）
```

## 全局语境 context

在生成数据的时候，许多地方会被视作 python 语句，脚本会使用 `eval()` 函数计算其实际值，同时，为了使脚本更加方便，eval 时会传入一个语境对象，包含了许多有用的变量可以调用

|变量名|类型|说明|
|---|---|---|
|env|object|用户自定义的变量|
|fake|Faker object|预生成的 Faker 对象|
|xeger|function|Xeger 对象中的一个成员函数|
|random|Module|Python 内置的 random 库|
|line|object|存有当前行的数据对象|

### line 对象的限制

由于脚本是按列生成数据的，并且位置靠前的列会优先被生成，并且 line 对象所能够引用的只有已经生成的列的数据，而有时候靠前的数据列也需要依据靠后的列进行条件判断等，此时可以在生成器声明中加上 `order` 选项

所有生成器的默认 `order` 均为`0`，若 `order` 有不同，则 `order` 更小的列优先生成，且相同 `order` 的列会由前到后依次生成

例如：若需要某一列最先生成，可以将 `order` 设为`-1`

**要注意的是**，`order` 的大小不影响最终呈现在数据表中的顺序，最终呈现的顺序永远是依照 schema 中书写的由上到下的顺序，`order` 只能决定每一列生成的顺序

## 字段生成条件

对于每一个字段，默认支持了多个生成器，只需要用列表的方式写出每个生成器即可

if 选项内的字符串也会被视作 python 语句，并且也可以调用全局语境内的任意变量

每一个生成器都可以配置一个 if 选项，某一个生成器不生效时则会顺延至下一个生成器，若该字段已声明的所有生成器都不生效时，脚本会采用一个隐式的 none 生成器，即不生成任何内容

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

> 上面的例子中若把 is_adult 与 age 互换位置则会发生错误，因为 age 使用到了 line 对象，且此时 is_adult 还没有生成。可选的解决方案是在 is_adult 中显式的声明 order 为-1，让 is_adult 先生成

善用 if 选项可以让假数据也有一定的逻辑性，但在实际工程中是否应该使用则见仁见智

- 逻辑错误的假数据也能够一定程度上反映出某些系统对错误处理的能力
- 如果系统的输入中已经有了完善的逻辑检查（即保证了数据库中的数据理一定是符合逻辑的），此时使用 if 选项可以避免系统处理不可能存在的逻辑错误
