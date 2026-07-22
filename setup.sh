#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
#  PhoneXtract v5.0  –  Linux / WSL / Ubuntu Setup Script
#  Created by : Aryan Singh Tarinai
# ─────────────────────────────────────────────────────────────

set -e

GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

VENV_DIR="venv"

echo -e "${GREEN}================================================${NC}"
echo -e "${CYAN}  PhoneXtract v5.0 - Setup Script${NC}"
echo -e "${CYAN}  Created by : Aryan Singh Tarinai${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""

# ── Check Python 3 ──────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!] Python3 not found. Installing...${NC}"
    sudo apt-get update -y && sudo apt-get install -y python3 python3-venv python3-pip
else
    PY_VER=$(python3 --version 2>&1)
    echo -e "${GREEN}[+] Found: $PY_VER${NC}"
fi

# ── Ensure python3-venv is available ─────────────────────────
if ! python3 -m venv --help &>/dev/null 2>&1; then
    echo -e "${YELLOW}[~] python3-venv not found. Installing...${NC}"
    sudo apt-get install -y python3-venv
fi

# ── Create virtual environment ───────────────────────────────
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${CYAN}[*] Creating virtual environment in ./$VENV_DIR ...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}[+] Virtual environment created.${NC}"
else
    echo -e "${YELLOW}[~] Virtual environment already exists. Skipping creation.${NC}"
fi

# ── Install / upgrade dependencies inside venv ───────────────
echo -e "${CYAN}[*] Installing Python dependencies into venv...${NC}"
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -r requirements.txt

# ── Create run.sh launcher ───────────────────────────────────
cat > run.sh << 'EOF'
#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$DIR/venv/bin/python3" "$DIR/phonextract.py" "$@"
EOF
chmod +x run.sh
chmod +x phonextract.py

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}[+] Setup complete!  PhoneXtract v5.0 ready.${NC}"
echo ""
echo -e "${CYAN}  Interactive menu:${NC}"
echo -e "${YELLOW}      bash run.sh${NC}"
echo -e "${CYAN}  Direct CLI usage:${NC}"
echo -e "${YELLOW}      bash run.sh +919876543210${NC}"
echo -e "${YELLOW}      bash run.sh +919876543210 --save --json${NC}"
echo -e "${YELLOW}      bash run.sh --batch numbers.txt${NC}"
echo -e "${GREEN}================================================${NC}"
