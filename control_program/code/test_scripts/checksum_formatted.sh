echo -n "Number of relays to be turned on: "

python3 checksum_formatted.py | xclip -selection clipboard

xclip -out -selection clipboard
