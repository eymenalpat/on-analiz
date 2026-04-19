#!/usr/bin/env bash
# on-analiz skill tek adımlı kurulum scripti
# Kullanım:
#   curl -sSL https://raw.githubusercontent.com/eymenalpat/on-analiz/main/install.sh | bash
#
# Bu script sadece dosyaları indirir. API key'leri /on-analiz ilk çalıştığında
# Claude içinden interaktif olarak istenir — hiç terminal komutu yazmanıza gerek yok.

set -e

REPO_URL="${ON_ANALIZ_REPO_URL:-https://github.com/eymenalpat/on-analiz.git}"
SKILL_DIR="$HOME/.claude/skills/on-analiz"

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}i${NC} $1"; }
success() { echo -e "${GREEN}✓${NC} $1"; }
warn()    { echo -e "${YELLOW}⚠${NC} $1"; }
fail()    { echo -e "${RED}✗${NC} $1"; exit 1; }

echo ""
echo "╭──────────────────────────────────────────╮"
echo "│  on-analiz skill kurulumu                │"
echo "╰──────────────────────────────────────────╯"
echo ""

# Gereksinim: git
command -v git >/dev/null 2>&1 || fail "git kurulu değil. Xcode Command Line Tools: xcode-select --install"

# Skill dizini
if [ -d "$SKILL_DIR" ]; then
  warn "$SKILL_DIR zaten var."
  read -p "Güncellemek ister misin? (.env ve cikti/ korunur) [y/N]: " REPLY </dev/tty
  if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
    info "kurulum iptal edildi"
    exit 0
  fi
  # .env ve cikti/ yedekle
  [ -f "$SKILL_DIR/.env" ] && cp "$SKILL_DIR/.env" /tmp/on-analiz-env-backup
  [ -d "$SKILL_DIR/cikti" ] && mv "$SKILL_DIR/cikti" /tmp/on-analiz-cikti-backup

  git -C "$SKILL_DIR" fetch --quiet
  git -C "$SKILL_DIR" reset --hard origin/main --quiet

  [ -f /tmp/on-analiz-env-backup ] && cp /tmp/on-analiz-env-backup "$SKILL_DIR/.env" && chmod 600 "$SKILL_DIR/.env"
  [ -d /tmp/on-analiz-cikti-backup ] && mv /tmp/on-analiz-cikti-backup "$SKILL_DIR/cikti"
  success "skill güncellendi"
else
  mkdir -p "$HOME/.claude/skills"
  info "skill indiriliyor..."
  git clone --quiet "$REPO_URL" "$SKILL_DIR" || fail "git clone başarısız: $REPO_URL"
  success "skill indirildi → $SKILL_DIR"
fi

# Railway CLI (opsiyonel — sadece public URL üretmek isteyenler için)
if ! command -v railway >/dev/null 2>&1; then
  info "Railway CLI bulunamadı (opsiyonel — sadece public link üretmek istersen gerekir)"
  if command -v brew >/dev/null 2>&1; then
    read -p "Homebrew ile şimdi kuralım mı? [y/N]: " REPLY </dev/tty
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
      brew install railway && success "railway kuruldu"
    fi
  elif command -v npm >/dev/null 2>&1; then
    read -p "npm ile şimdi kuralım mı? [y/N]: " REPLY </dev/tty
    if [[ "$REPLY" =~ ^[Yy]$ ]]; then
      npm install -g @railway/cli && success "railway kuruldu"
    fi
  fi
else
  success "railway CLI zaten kurulu"
fi

echo ""
echo "╭──────────────────────────────────────────╮"
echo "│  Kurulum tamamlandı                      │"
echo "╰──────────────────────────────────────────╯"
echo ""
echo "Sonraki adım:"
echo ""
echo "  1. Claude Code'u aç (veya yeniden başlat)"
echo -e "  2. Yeni konuşmada şunu yaz:  ${GREEN}/on-analiz${NC}"
echo ""
echo "Gereken API key'leri Claude sana soracak. Başka komut yazmana gerek yok."
echo ""
