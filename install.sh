#!/data/data/com.termux/files/usr/bin/bash

set -e

REPO="https://github.com/USERNAME/bankai-downloader"

pkg update -y
pkg install -y python ffmpeg git curl

mkdir -p $HOME/.bankai
cd $HOME/.bankai

curl -LO https://raw.githubusercontent.com/USERNAME/bankai-downloader/main/requirements.txt
curl -LO https://raw.githubusercontent.com/USERNAME/bankai-downloader/main/bankai_downloader.py

pip install -r requirements.txt

cat > $PREFIX/bin/bankai << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python $HOME/.bankai/bankai_downloader.py "$@"
EOF

chmod +x $PREFIX/bin/bankai

echo "Installed! Run: bankai"
