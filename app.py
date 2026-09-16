"""
CrypTool - Interactive Cryptography Toolkit

Covers:
- Caesar Cipher (mono-alphabetic substitution)
- Vigenere Cipher (poly-alphabetic substitution)
- One-Time Pad
- Rail Fence Cipher (transposition)
- Columnar Transposition Cipher
- Steganography (hiding text inside an image)
- Hashing (MD5, SHA-1, SHA-256)
- Symmetric Encryption (AES, DES)
- Asymmetric Encryption (RSA)
- Digital Signature (RSA sign/verify)

Run locally with:  streamlit run app.py
"""

import streamlit as st
import string
import random
import hashlib
import base64
import io

from Crypto.Cipher import AES, DES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

from PIL import Image
import numpy as np


# ======================================================================
#  PAGE CONFIG & STYLING
# ======================================================================
st.set_page_config(
    page_title="CrypTool | Cryptography Toolkit",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .stApp {
        background-color: #f4f7fb;
        background-image:
            linear-gradient(rgba(15,23,42,0.035) 1px, transparent 1px),
            linear-gradient(90deg, rgba(15,23,42,0.035) 1px, transparent 1px);
        background-size: 28px 28px;
    }
    h1, h2, h3, h4 {
        color: #0f172a !important;
        font-family: 'Courier New', monospace;
    }
    p, label, .stMarkdown, span {
        color: #334155;
    }
    .main-title {
        text-align: center;
        font-size: 2.6rem;
        font-weight: 800;
        font-family: 'Courier New', monospace;
        letter-spacing: 1px;
        background: -webkit-linear-gradient(45deg, #0891b2, #4f46e5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding-bottom: 0px;
    }
    .sub-title {
        text-align: center;
        color: #64748b !important;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
        font-family: 'Courier New', monospace;
    }
    .result-box {
        background-color: #ecfeff;
        border: 1px solid #06b6d4;
        border-left: 4px solid #0891b2;
        border-radius: 8px;
        padding: 16px;
        margin-top: 10px;
        word-wrap: break-word;
        font-family: 'Courier New', monospace;
        color: #0e7490;
        font-size: 0.95rem;
    }
    .info-box {
        background-color: #eef2ff;
        border-left: 4px solid #6366f1;
        border-radius: 6px;
        padding: 12px 16px;
        margin-bottom: 12px;
        color: #3730a3 !important;
        font-size: 0.88rem;
    }
    div.stButton > button {
        background: linear-gradient(90deg, #0891b2, #4f46e5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        width: 100%;
        font-family: 'Courier New', monospace;
        box-shadow: 0 2px 6px rgba(79,70,229,0.25);
    }
    div.stButton > button:hover {
        background: linear-gradient(90deg, #0e7490, #4338ca);
        color: white;
    }
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    section[data-testid="stSidebar"] * {
        color: #1e293b;
    }
    .stTextInput input, .stTextArea textarea, .stNumberInput input {
        background-color: #ffffff !important;
        color: #0f172a !important;
        border-radius: 6px !important;
        border: 1px solid #cbd5e1 !important;
        font-family: 'Courier New', monospace !important;
    }
    div[data-testid="stExpander"] {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    code, .stCodeBlock {
        font-family: 'Courier New', monospace !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ======================================================================
#  HELPER: display a result nicely
# ======================================================================
def show_result(label, value):
    st.markdown(f"**{label}**")
    st.markdown(f"<div class='result-box'>{value}</div>", unsafe_allow_html=True)


def info(text):
    st.markdown(f"<div class='info-box'>ℹ️ {text}</div>", unsafe_allow_html=True)


# ======================================================================
#  1. CAESAR CIPHER  (Mono-alphabetic - fixed shift)
# ======================================================================
def caesar_encrypt(text, shift):
    result = ""
    for ch in text:
        if ch.isupper():
            result += chr((ord(ch) - 65 + shift) % 26 + 65)
        elif ch.islower():
            result += chr((ord(ch) - 97 + shift) % 26 + 97)
        else:
            result += ch
    return result


def caesar_decrypt(text, shift):
    return caesar_encrypt(text, -shift)


# ======================================================================
#  2. MONO-ALPHABETIC CIPHER (random substitution using a key alphabet)
# ======================================================================
def generate_mono_key(seed_word=""):
    alphabet = list(string.ascii_uppercase)
    rng = random.Random(seed_word if seed_word else None)
    shuffled = alphabet.copy()
    rng.shuffle(shuffled)
    return "".join(shuffled)


def mono_encrypt(text, key):
    plain = string.ascii_uppercase
    mapping = {p: k for p, k in zip(plain, key)}
    result = ""
    for ch in text.upper():
        if ch in mapping:
            result += mapping[ch]
        else:
            result += ch
    return result


def mono_decrypt(text, key):
    plain = string.ascii_uppercase
    mapping = {k: p for p, k in zip(plain, key)}
    result = ""
    for ch in text.upper():
        if ch in mapping:
            result += mapping[ch]
        else:
            result += ch
    return result


# ======================================================================
#  3. VIGENERE CIPHER (Poly-alphabetic substitution)
# ======================================================================
def vigenere_encrypt(text, key):
    key = key.upper()
    result = ""
    j = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[j % len(key)]) - 65
            base = 65 if ch.isupper() else 97
            result += chr((ord(ch) - base + shift) % 26 + base)
            j += 1
        else:
            result += ch
    return result


def vigenere_decrypt(text, key):
    key = key.upper()
    result = ""
    j = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[j % len(key)]) - 65
            base = 65 if ch.isupper() else 97
            result += chr((ord(ch) - base - shift) % 26 + base)
            j += 1
        else:
            result += ch
    return result


# ======================================================================
#  4. ONE-TIME PAD  (key must be same length as text, used once)
# ======================================================================
def generate_otp_key(length):
    return "".join(random.choice(string.ascii_uppercase) for _ in range(length))


def otp_encrypt(text, key):
    text = text.upper().replace(" ", "")
    result = ""
    for t, k in zip(text, key):
        result += chr((ord(t) - 65 + ord(k) - 65) % 26 + 65)
    return result


def otp_decrypt(cipher, key):
    result = ""
    for c, k in zip(cipher, key):
        result += chr((ord(c) - 65 - (ord(k) - 65)) % 26 + 65)
    return result


# ======================================================================
#  5. RAIL FENCE CIPHER (Transposition)
# ======================================================================
def railfence_encrypt(text, rails):
    fence = [[] for _ in range(rails)]
    rail, direction = 0, 1
    for ch in text:
        fence[rail].append(ch)
        if rail == 0:
            direction = 1
        elif rail == rails - 1:
            direction = -1
        rail += direction
    return "".join("".join(row) for row in fence)


def railfence_decrypt(cipher, rails):
    pattern = list(range(rails)) + list(range(rails - 2, 0, -1))
    if rails == 1:
        return cipher
    order = [pattern[i % len(pattern)] for i in range(len(cipher))]
    # Determine how many chars go into each rail
    rail_counts = [order.count(r) for r in range(rails)]
    rail_chars = []
    idx = 0
    for count in rail_counts:
        rail_chars.append(list(cipher[idx: idx + count]))
        idx += count
    result = []
    rail_pos = [0] * rails
    for r in order:
        result.append(rail_chars[r][rail_pos[r]])
        rail_pos[r] += 1
    return "".join(result)


# ======================================================================
#  6. COLUMNAR TRANSPOSITION CIPHER
# ======================================================================
def columnar_encrypt(text, key):
    text = text.replace(" ", "")
    key_order = sorted(range(len(key)), key=lambda k: key[k])
    n_cols = len(key)
    n_rows = -(-len(text) // n_cols)  # ceil division
    padded = text.ljust(n_rows * n_cols, "X")
    grid = [padded[i:i + n_cols] for i in range(0, len(padded), n_cols)]
    cipher = ""
    for col in key_order:
        for row in grid:
            cipher += row[col]
    return cipher


def columnar_decrypt(cipher, key):
    n_cols = len(key)
    n_rows = -(-len(cipher) // n_cols)
    key_order = sorted(range(len(key)), key=lambda k: key[k])
    col_len = n_rows
    cols = [""] * n_cols
    idx = 0
    for col in key_order:
        cols[col] = cipher[idx: idx + col_len]
        idx += col_len
    grid = []
    for r in range(n_rows):
        row = "".join(cols[c][r] if r < len(cols[c]) else "" for c in range(n_cols))
        grid.append(row)
    return "".join(grid).rstrip("X")


# ======================================================================
#  7. STEGANOGRAPHY (hide text inside PNG image using LSB)
# ======================================================================
def stego_encode(image: Image.Image, secret_text: str) -> Image.Image:
    secret_text += "#####"  # end marker
    binary_secret = "".join(format(ord(c), "08b") for c in secret_text)
    img = image.convert("RGB")
    arr = np.array(img)
    flat = arr.flatten()

    if len(binary_secret) > len(flat):
        raise ValueError("Message too long for this image.")

    for i, bit in enumerate(binary_secret):
        flat[i] = (flat[i] & 0b11111110) | int(bit)

    new_arr = flat.reshape(arr.shape)
    return Image.fromarray(new_arr.astype("uint8"), "RGB")


def stego_decode(image: Image.Image) -> str:
    img = image.convert("RGB")
    arr = np.array(img).flatten()
    bits = [str(pixel & 1) for pixel in arr]
    chars = []
    for i in range(0, len(bits) - 8, 8):
        byte = "".join(bits[i:i + 8])
        chars.append(chr(int(byte, 2)))
        decoded = "".join(chars)
        if decoded.endswith("#####"):
            return decoded[:-5]
    return "".join(chars)


# ======================================================================
#  8. HASHING
# ======================================================================
def compute_hash(text, algo):
    data = text.encode()
    if algo == "MD5":
        return hashlib.md5(data).hexdigest()
    elif algo == "SHA-1":
        return hashlib.sha1(data).hexdigest()
    elif algo == "SHA-256":
        return hashlib.sha256(data).hexdigest()


# ======================================================================
#  9. SYMMETRIC ENCRYPTION (AES / DES)
# ======================================================================
def symmetric_encrypt(text, key, algo):
    data = text.encode()
    if algo == "AES":
        key_bytes = key.encode("utf-8").ljust(16, b"0")[:16]
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        ct = cipher.encrypt(pad(data, AES.block_size))
    else:  # DES
        key_bytes = key.encode("utf-8").ljust(8, b"0")[:8]
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        ct = cipher.encrypt(pad(data, DES.block_size))
    return base64.b64encode(ct).decode()


def symmetric_decrypt(cipher_b64, key, algo):
    ct = base64.b64decode(cipher_b64)
    if algo == "AES":
        key_bytes = key.encode("utf-8").ljust(16, b"0")[:16]
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
    else:  # DES
        key_bytes = key.encode("utf-8").ljust(8, b"0")[:8]
        cipher = DES.new(key_bytes, DES.MODE_ECB)
        pt = unpad(cipher.decrypt(ct), DES.block_size)
    return pt.decode()


# ======================================================================
#  10. ASYMMETRIC ENCRYPTION (RSA)
# ======================================================================
def generate_rsa_keys():
    key = RSA.generate(2048)
    private_key = key.export_key()
    public_key = key.publickey().export_key()
    return private_key, public_key


def rsa_encrypt(text, public_key_pem):
    key = RSA.import_key(public_key_pem)
    cipher = PKCS1_OAEP.new(key)
    ct = cipher.encrypt(text.encode())
    return base64.b64encode(ct).decode()


def rsa_decrypt(cipher_b64, private_key_pem):
    key = RSA.import_key(private_key_pem)
    cipher = PKCS1_OAEP.new(key)
    pt = cipher.decrypt(base64.b64decode(cipher_b64))
    return pt.decode()


# ======================================================================
#  11. DIGITAL SIGNATURE (RSA sign / verify)
# ======================================================================
def rsa_sign(text, private_key_pem):
    key = RSA.import_key(private_key_pem)
    h = SHA256.new(text.encode())
    signature = pkcs1_15.new(key).sign(h)
    return base64.b64encode(signature).decode()


def rsa_verify(text, signature_b64, public_key_pem):
    key = RSA.import_key(public_key_pem)
    h = SHA256.new(text.encode())
    signature = base64.b64decode(signature_b64)
    try:
        pkcs1_15.new(key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


# ======================================================================
#  UI — SIDEBAR NAVIGATION
# ======================================================================
st.markdown("<div class='main-title'>🔐 CrypTool</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>Encrypt · Decrypt · Explore — a hands-on cryptography playground</div>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("## 🧭 Choose a Module")
module = st.sidebar.radio(
    "",
    [
        "🏠 Home",
        "🔤 Caesar Cipher",
        "🔀 Mono-alphabetic Cipher",
        "🔁 Vigenere Cipher (Poly-alphabetic)",
        "🎲 One-Time Pad",
        "🚂 Rail Fence Cipher",
        "📐 Columnar Transposition",
        "🖼️ Steganography",
        "#️⃣ Hashing (MD5/SHA)",
        "🔒 Symmetric Encryption (AES/DES)",
        "🔑 Asymmetric Encryption (RSA)",
        "✍️ Digital Signature",
    ],
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div class='info-box'>A collection of classic and modern cryptography "
    "techniques you can try out live, with hands-on demos.</div>",
    unsafe_allow_html=True,
)

# ======================================================================
#  HOME
# ======================================================================
if module == "🏠 Home":
    st.markdown("### Welcome 👋")
    info(
        "This tool lets you **encrypt, decrypt, and understand** every cryptography "
        "cryptography technique — Caesar cipher, substitution, "
        "transposition, steganography, hashing, symmetric/asymmetric encryption, "
        "and digital signatures. Pick a module from the sidebar to begin."
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("#### 🔤 Substitution")
        st.write("Caesar, Mono-alphabetic, Vigenere, One-Time Pad")
    with col2:
        st.markdown("#### 🚂 Transposition")
        st.write("Rail Fence, Columnar Transposition")
    with col3:
        st.markdown("#### 🔒 Modern Crypto")
        st.write("Hashing, AES/DES, RSA, Digital Signatures")

# ======================================================================
#  CAESAR CIPHER
# ======================================================================
elif module == "🔤 Caesar Cipher":
    st.markdown("## 🔤 Caesar Cipher")
    info("Each letter is shifted by a fixed number of positions in the alphabet. "
         "Example: shift=3 → A becomes D.")

    text = st.text_area("Enter text", "Attack at dawn")
    shift = st.slider("Shift value (key)", 1, 25, 3)
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Caesar Cipher"):
        if action == "Encrypt":
            show_result("Encrypted Text", caesar_encrypt(text, shift))
        else:
            show_result("Decrypted Text", caesar_decrypt(text, shift))

# ======================================================================
#  MONO-ALPHABETIC CIPHER
# ======================================================================
elif module == "🔀 Mono-alphabetic Cipher":
    st.markdown("## 🔀 Mono-alphabetic Substitution Cipher")
    info("Every letter of the alphabet is replaced by another letter, based on a "
         "fixed substitution key (a full 26-letter shuffled alphabet).")

    if "mono_key" not in st.session_state:
        st.session_state.mono_key = generate_mono_key()

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Generate New Key"):
            st.session_state.mono_key = generate_mono_key()

    st.text_input("Substitution Key (A→...)", st.session_state.mono_key, disabled=True)
    text = st.text_area("Enter text", "Hello World")
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Mono-alphabetic Cipher"):
        if action == "Encrypt":
            show_result("Encrypted Text", mono_encrypt(text, st.session_state.mono_key))
        else:
            show_result("Decrypted Text", mono_decrypt(text, st.session_state.mono_key))

# ======================================================================
#  VIGENERE CIPHER
# ======================================================================
elif module == "🔁 Vigenere Cipher (Poly-alphabetic)":
    st.markdown("## 🔁 Vigenere Cipher")
    info("A poly-alphabetic cipher that uses a keyword to shift each letter by a "
         "different amount, repeating the keyword across the text.")

    text = st.text_area("Enter text", "Attack at dawn")
    key = st.text_input("Keyword", "LEMON")
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Vigenere Cipher"):
        if not key.isalpha():
            st.error("Key must contain only letters.")
        elif action == "Encrypt":
            show_result("Encrypted Text", vigenere_encrypt(text, key))
        else:
            show_result("Decrypted Text", vigenere_decrypt(text, key))

# ======================================================================
#  ONE-TIME PAD
# ======================================================================
elif module == "🎲 One-Time Pad":
    st.markdown("## 🎲 One-Time Pad (OTP)")
    info("A truly unbreakable cipher when the key is random, kept secret, and used "
         "only once, and is the same length as the message.")

    text = st.text_input("Enter text (letters only, no spaces)", "HELLO").upper().replace(" ", "")
    text = "".join(ch for ch in text if ch.isalpha())

    if "otp_key" not in st.session_state or len(st.session_state.otp_key) != len(text):
        st.session_state.otp_key = generate_otp_key(len(text)) if text else ""

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Generate New Key") and text:
            st.session_state.otp_key = generate_otp_key(len(text))

    st.text_input("Random Key (auto-generated, same length as text)", st.session_state.otp_key, disabled=True)

    if st.button("Encrypt with OTP"):
        if text:
            cipher = otp_encrypt(text, st.session_state.otp_key)
            show_result("Encrypted Text", cipher)
            show_result("Decrypted back (verification)", otp_decrypt(cipher, st.session_state.otp_key))
        else:
            st.error("Please enter some text first.")

# ======================================================================
#  RAIL FENCE CIPHER
# ======================================================================
elif module == "🚂 Rail Fence Cipher":
    st.markdown("## 🚂 Rail Fence Cipher")
    info("A transposition cipher where letters are written in a zig-zag pattern "
         "across a number of 'rails' and then read off row by row.")

    text = st.text_area("Enter text (no spaces recommended)", "WEAREDISCOVEREDFLEEATONCE")
    rails = st.slider("Number of rails (key)", 2, 10, 3)
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Rail Fence Cipher"):
        clean_text = text.replace(" ", "")
        if action == "Encrypt":
            show_result("Encrypted Text", railfence_encrypt(clean_text, rails))
        else:
            show_result("Decrypted Text", railfence_decrypt(clean_text, rails))

# ======================================================================
#  COLUMNAR TRANSPOSITION
# ======================================================================
elif module == "📐 Columnar Transposition":
    st.markdown("## 📐 Columnar Transposition Cipher")
    info("Plaintext is written in rows under a keyword, then columns are read off "
         "in the alphabetical order of the keyword's letters.")

    text = st.text_area("Enter text", "HELLOWORLDTHISISCRYPTOGRAPHY")
    key = st.text_input("Keyword (no repeating letters ideally)", "ZEBRA")
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Columnar Transposition"):
        if not key.isalpha():
            st.error("Key must contain only letters.")
        elif action == "Encrypt":
            show_result("Encrypted Text", columnar_encrypt(text, key))
        else:
            show_result("Decrypted Text", columnar_decrypt(text, key))

# ======================================================================
#  STEGANOGRAPHY
# ======================================================================
elif module == "🖼️ Steganography":
    st.markdown("## 🖼️ Steganography")
    info("Hides a secret message inside the pixels of an image (LSB technique) "
         "so the image looks unchanged to the naked eye.")

    tab1, tab2 = st.tabs(["🙈 Hide Message", "🔍 Reveal Message"])

    with tab1:
        uploaded = st.file_uploader("Upload a PNG image", type=["png", "bmp"], key="hide_img")
        secret = st.text_area("Secret message to hide", "This is a secret message!")
        if uploaded and st.button("Hide Message in Image"):
            try:
                img = Image.open(uploaded)
                encoded_img = stego_encode(img, secret)
                buf = io.BytesIO()
                encoded_img.save(buf, format="PNG")
                st.image(encoded_img, caption="Image with hidden message", width=300)
                st.download_button(
                    "⬇️ Download Encoded Image",
                    data=buf.getvalue(),
                    file_name="stego_image.png",
                    mime="image/png",
                )
            except ValueError as e:
                st.error(str(e))

    with tab2:
        uploaded2 = st.file_uploader("Upload the encoded PNG image", type=["png", "bmp"], key="reveal_img")
        if uploaded2 and st.button("Reveal Hidden Message"):
            img = Image.open(uploaded2)
            hidden_text = stego_decode(img)
            show_result("Hidden Message", hidden_text)

# ======================================================================
#  HASHING
# ======================================================================
elif module == "#️⃣ Hashing (MD5/SHA)":
    st.markdown("## #️⃣ Hashing")
    info("A one-way function that converts data into a fixed-size digest. "
         "Used for integrity checking — cannot be reversed back to original data.")

    text = st.text_area("Enter text to hash", "Hello, World!")
    algo = st.selectbox("Hashing Algorithm", ["MD5", "SHA-1", "SHA-256"])

    if st.button("Generate Hash"):
        show_result(f"{algo} Hash", compute_hash(text, algo))

    st.markdown("#### ✅ Verify Integrity")
    text2 = st.text_area("Enter text to verify", "Hello, World!", key="verify_text")
    given_hash = st.text_input("Paste hash to compare against")
    if st.button("Verify Hash"):
        computed = compute_hash(text2, algo)
        if computed == given_hash.strip().lower():
            st.success("✅ Match — data integrity verified!")
        else:
            st.error("❌ No match — data may have been altered.")

# ======================================================================
#  SYMMETRIC ENCRYPTION
# ======================================================================
elif module == "🔒 Symmetric Encryption (AES/DES)":
    st.markdown("## 🔒 Symmetric Key Encryption")
    info("Same key is used for both encryption and decryption. "
         "AES (Advanced Encryption Standard) is modern and secure; "
         "DES (Data Encryption Standard) is older, shown here for reference.")

    algo = st.selectbox("Algorithm", ["AES", "DES"])
    key_len_note = "16 characters (or will be padded)" if algo == "AES" else "8 characters (or will be padded)"
    text = st.text_area("Plain text", "This is a secret message")
    key = st.text_input(f"Secret Key ({key_len_note})", "mysecret")
    action = st.radio("Action", ["Encrypt", "Decrypt"], horizontal=True)

    if st.button("Run Symmetric Cipher"):
        try:
            if action == "Encrypt":
                show_result("Encrypted (Base64)", symmetric_encrypt(text, key, algo))
            else:
                show_result("Decrypted Text", symmetric_decrypt(text, key, algo))
        except Exception as e:
            st.error(f"Error: {e}")

# ======================================================================
#  ASYMMETRIC ENCRYPTION (RSA)
# ======================================================================
elif module == "🔑 Asymmetric Encryption (RSA)":
    st.markdown("## 🔑 Asymmetric Encryption — RSA")
    info("Uses a key **pair**: a public key (for encryption, shareable) and a "
         "private key (for decryption, kept secret).")

    if "rsa_private" not in st.session_state:
        st.session_state.rsa_private, st.session_state.rsa_public = generate_rsa_keys()

    if st.button("🔄 Generate New RSA Key Pair (2048-bit)"):
        st.session_state.rsa_private, st.session_state.rsa_public = generate_rsa_keys()

    with st.expander("🔓 Public Key"):
        st.code(st.session_state.rsa_public.decode())
    with st.expander("🔒 Private Key (keep secret!)"):
        st.code(st.session_state.rsa_private.decode())

    text = st.text_area("Message to encrypt", "Top secret data")
    if st.button("Encrypt with Public Key"):
        try:
            ct = rsa_encrypt(text, st.session_state.rsa_public)
            st.session_state.rsa_cipher = ct
            show_result("Encrypted (Base64)", ct)
        except Exception as e:
            st.error(f"Error: {e}")

    cipher_input = st.text_area(
        "Cipher text to decrypt",
        st.session_state.get("rsa_cipher", ""),
    )
    if st.button("Decrypt with Private Key"):
        try:
            pt = rsa_decrypt(cipher_input, st.session_state.rsa_private)
            show_result("Decrypted Text", pt)
        except Exception as e:
            st.error(f"Error: {e}")

# ======================================================================
#  DIGITAL SIGNATURE
# ======================================================================
elif module == "✍️ Digital Signature":
    st.markdown("## ✍️ Digital Signature")
    info("The sender signs a message with their **private key**. Anyone with the "
         "**public key** can verify the signature — proving authenticity and integrity.")

    if "dsig_private" not in st.session_state:
        st.session_state.dsig_private, st.session_state.dsig_public = generate_rsa_keys()

    if st.button("🔄 Generate New Signing Key Pair"):
        st.session_state.dsig_private, st.session_state.dsig_public = generate_rsa_keys()

    with st.expander("🔓 Public Key (share with verifier)"):
        st.code(st.session_state.dsig_public.decode())
    with st.expander("🔒 Private Key (signer keeps secret)"):
        st.code(st.session_state.dsig_private.decode())

    msg = st.text_area("Message to sign", "This message is authentic.")
    if st.button("✍️ Sign Message"):
        sig = rsa_sign(msg, st.session_state.dsig_private)
        st.session_state.dsig_signature = sig
        show_result("Digital Signature (Base64)", sig)

    st.markdown("#### ✅ Verify Signature")
    verify_msg = st.text_area("Message to verify", msg, key="verify_msg")
    sig_input = st.text_area("Signature to verify", st.session_state.get("dsig_signature", ""))
    if st.button("Verify Signature"):
        valid = rsa_verify(verify_msg, sig_input, st.session_state.dsig_public)
        if valid:
            st.success("✅ Signature is VALID — message is authentic and unaltered.")
        else:
            st.error("❌ Signature is INVALID — message may be tampered or key mismatch.")

# ======================================================================
#  FOOTER
# ======================================================================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#64748b; font-size:0.8rem;'>"
    "CrypTool — encrypt, decrypt, and understand how cryptography really works 🔐"
    "</p>",
    unsafe_allow_html=True,
)
