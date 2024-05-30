echo -n "Data to be converted to Arduino format: "

python3 checksum_unformatted.py | xclip -selection clipboard

xclip -out -selection clipboard
