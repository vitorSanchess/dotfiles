# Dotfiles

Personal Linux configuration files managed with [GNU Stow](https://www.gnu.org/software/stow/).

## Included Packages

- **Shells & Git:** `bash`, `zsh`, `fish`, `git`
- **Window Managers & Bars:** `niri`, `noctalia`, `hypr`, `waybar`, `rofi`, `openbox`, `tint2`
- **Terminals & CLI Tools:** `alacritty`, `kitty`, `fastfetch`, `btop`
- **Editors & Apps:** `zed`, `micro`, `spotifast`, `zapfast`

## Usage

Clone this repository into `~/dotfiles`:

```bash
git clone <repo-url> ~/dotfiles
cd ~/dotfiles
```

### Symlink all packages

```bash
stow -t ~ bash zsh git fish niri noctalia hypr waybar rofi openbox tint2 alacritty kitty fastfetch btop zed micro spotifast zapfast
```

### Symlink a single package

```bash
stow -t ~ niri
```
