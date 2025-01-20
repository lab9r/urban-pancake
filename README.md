# AppImageDesktop


## ubuntu dependency
```
sudo apt install libfuse2 -y
 ```

## uninstall

```
# find files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*"

# delete files
find . ~/.local/share/applications ~/.local/share/icons -iname "*obsidian*" --delete
```