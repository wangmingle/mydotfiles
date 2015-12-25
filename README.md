My Dotfiles

=========================

Usage:

# gitopen 使用本地默认浏览器打开git url

打开当前git

```bash
    gitopen
```
从master分支pull下来与当前分之合并

```bash
    gitopen -p 
````

从dev分支pull下来与当前分之合并

```bash
    gitopen -p dev
````

比较当前分之与最后一次提交有什么不同

```bash
    gitopen --tip
```

比较dev分支与最后一次提交有什么不同

```bash
    gitopen --tip dev
```

pull所有的分支 或者使用 -s

```bash
    gitopen --pulls
```


Installed:

1. git clone https://github.com/wangmingle/mydotfiles.git

2. Add index to ~/.bash_profile

   source ~/dotfiles/index 

3. source ~/.bash_profile
