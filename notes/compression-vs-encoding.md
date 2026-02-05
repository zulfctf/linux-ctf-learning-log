# Compression vs Encoding (Base64)

While working through Linux and CTF-style challenges, I spent a long time
confusing compressed binary data with encoded text.

## What confused me
- The files were binary and compressed, so I assumed they needed decoding
- Running base64 decode produced large amounts of meaningless output
- I kept extracting archives in loops without understanding the layers

## What I learned
- Base64 is a text encoding, not a compression method
- Most binary files on disk are not base64-encoded
- The correct approach is to identify each file format before acting

## Tools that helped
- file
- xxd
- gunzip
- bunzip2
- tar

## Takeaway
Identify the format first. Guessing leads to noise and wasted time.
