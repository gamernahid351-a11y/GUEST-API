# -*- coding: utf-8 -*-
# ============================================================
#   MEHEDI GUEST GENERATOR — FLASK API
#   Same imports as x.py · Working ChooseRegion guest gen
#   Endpoint: /gen?count=N  |  /gen1  |  /health
# ============================================================
import sys, os, json, time, uuid, random, asyncio, base64, struct, socket
import string, hmac, hashlib, ssl, warnings, traceback
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import httpx
import aiohttp
from flask import Flask, request, jsonify

warnings.filterwarnings("ignore")

try:
    from google_play_scraper import app as play_scraper
except Exception:
    play_scraper = None

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ==================== CONFIG ====================
uVer        = "2018.4.12f1"
GameVer     = "2.132.4"
ReleaseVer  = "OB55"
UaUnity     = f"UnityPlayer/{uVer} (UnityWebRequest/1.0, libcurl/8.5.0-DEV)"
HEX_KEY     = "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3"
API_KEY     = HEX_KEY.encode()

REGION      = "BD"
LANG        = "bn"
NAME_PREFIX = "MEHEDI__"
MAX_COUNT   = 20
Threads     = 5

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

KEYSTREAM = bytes([0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,
                   0x31,0x37,0x30,0x30,0x30,0x30,0x30,0x32,0x30,0x31,0x37,0x30,0x30,0x30,
                   0x30,0x30,0x32,0x30])

REGION_LANG = {"ME":"ar","IND":"hi","ID":"id","VN":"vi","TH":"th","BD":"bn",
               "PK":"ur","TW":"zh","RU":"ru","SAC":"es","BR":"pt","NA":"pt",
               "SG":"pt","US":"pt"}

SharedCookie = (
    "datadome=nmP601L~4DvFBNemgIhE2d3Y~tR68_GHUaV8WhUdKLhjg74S_YsRWpOCnYL8cNtz"
    "58Olr_SEm1GSttQImpJO1j15k2AGGY~bFDp0hfrk6p0Dv_JZSGXJUGhhY_QsQ~5H"
)

UserAgents = [
    "GarenaMSDK/4.0.42(RMX3710 ;Android 15;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(RMX3085 ;Android 13;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(SM-A546E ;Android 14;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(SM-A235F ;Android 13;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(CPH2449 ;Android 14;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(V2307 ;Android 14;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(Pixel 6 ;Android 13;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(2201117TG  ;Android 14;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(NTH-NX9 ;Android 13;bn;BD;app 2.132.1 2019118525;)",
    "GarenaMSDK/4.0.42(X6836 ;Android 13;bn;BD;app 2.132.1 2019118525;)",
]

# x.py's exact blob (note: this is the WORKING one from x.py)
GGRE_RAW = bytes.fromhex(
    "47475245010101006d020000b260ee08e1f86b4c57f9c70f86bba26ed5d1436bcf52e142db3249d905eded757764991ca31a8373cdd26eab91b80f3f1f6f262f4f10b895d7b6937ddba30a27197453890e9da49373f736c679b8254e2f8e1623e91084a5fdd5374fe478ff99e010834553fddeb0bec4018d142e49df9bb236675b67e852f92a43586f7a7d4d0d7a197a1d4da32714dab4d069ad53214e2c33b3877420a12459738c4c619cbd815fa878bbd104776bb3e1ac7818d5397b04a666ac57f682763ff2df31bc2f846ddc7904f3dce1bda0c4b01f9698e9166f98c84f92640abe3f6317834a42e5c12573b46842c1a6ea8fe6ca9c006dca48a2087e1f983dfb5692771e4a0b15b337ad669b1d08b40862b176bace5331b49a767375b1a8469012aa70a67b55fe71b72478201d0b3ac7269c064c960361e92ee7ba8a42cc6b582bf9b965fb388fa9172ad44c4b073ac23c02080a6bcd106b691ffdf4c7cf71e42f2063fcf196e9bddc5e85be1fe5048eb1b31b460efbb46d76195eef9904c4cba326f2e17ff51fec17dd965aa06dadd4ab07d6966e4a7c38e8afd66dfde56c872bb87516a8f7313c797e4d80e5ad4a5f7afad95c1e0449254adae052e71a3fb98399f93ab30848e0d23252dd45e6fd41bc5fa7303dfb846a8fd713a0032a0b0ae96dfba1bbe41d20abd8099e2cb7fccc329d25bd153029139ef05d090a5093ea557693c0a8d491395b8a23ca844b3887dd5dfc29ac06f4b9be87883a793211b973465e2644c4f5de02b8ab01571401203fc2740423826858cc6da0194c195d27aac4ec4b9d23d506c1501d06440aca3fc180926d75d4a004d3dff21eb4ea1e8c86e6c9627248eff953e1d192d5c8efc006a7e512388ef2ebdb72ee3ad42d719f28e8f994e12ebf4c79f2ffe3abd7408ccd2236a7b89b2606247a732c10c4"
)

# httpx client (shared) — same as x.py
client = httpx.AsyncClient(verify=False, timeout=15.0)

# ==================== HELPERS (same as x.py) ====================
def encode_varint(n: int) -> bytes:
    out = bytearray()
    if n < 0: n &= 0xFFFFFFFFFFFFFFFF
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def _pb_varint(fn, val): return encode_varint((fn<<3)|0) + encode_varint(val)
def _pb_length(fn, val):
    enc = val.encode('utf-8') if isinstance(val,str) else val
    return encode_varint((fn<<3)|2) + encode_varint(len(enc)) + enc

def create_proto(fields) -> bytes:
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(field, str): field = int(field)
        if isinstance(value, dict):
            packet.extend(_pb_length(field, bytes(create_proto(value))))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    packet.extend(_pb_length(field, bytes(create_proto(item))))
                elif isinstance(item, str):
                    packet.extend(_pb_length(field, item))
                elif isinstance(item, (bytes, bytearray)):
                    packet.extend(_pb_length(field, bytes(item)))
                elif isinstance(item, bool):
                    packet.extend(_pb_varint(field, 1 if item else 0))
                elif isinstance(item, int):
                    packet.extend(_pb_varint(field, item))
        elif isinstance(value, bool):
            packet.extend(_pb_varint(field, 1 if value else 0))
        elif isinstance(value, int):
            packet.extend(_pb_varint(field, value))
        elif isinstance(value, str):
            packet.extend(_pb_length(field, value))
        elif isinstance(value, (bytes, bytearray)):
            packet.extend(_pb_length(field, bytes(value)))
    return bytes(packet)

def encrypt_aes(hex_data: str) -> str:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(bytes.fromhex(hex_data), AES.block_size)).hex()

def decode_varint(data, offset):
    result = 0; shift = 0
    while offset < len(data):
        byte = data[offset]
        result |= (byte & 0x7F) << shift
        offset += 1
        if not (byte & 0x80): return result, offset
        shift += 7
    return None, offset

def decode_protobuf_2(data):
    result = {}; offset = 0
    data_len = len(data)
    while offset < data_len:
        header, offset = decode_varint(data, offset)
        if header is None: break
        fn = header >> 3; wt = header & 0x7
        if wt == 0:
            v, offset = decode_varint(data, offset)
            if v is not None: result[fn] = v
        elif wt == 2:
            length, offset = decode_varint(data, offset)
            if length is None: break
            value = data[offset:offset+length]; offset += length
            try:
                s = value.decode('utf-8')
                result[fn] = s if s else value.hex()
            except UnicodeDecodeError:
                nested = decode_protobuf_2(value)
                result[fn] = nested if nested else value.hex()
        elif wt == 1: offset += 8
        elif wt == 3: offset += 4
        else: break
    return result

def encode_open_id(open_id):
    return bytes(ord(c) ^ KEYSTREAM[i % 32] for i, c in enumerate(open_id))

def make_name():
    chars = string.ascii_lowercase + string.digits
    return NAME_PREFIX + ''.join(random.choices(chars, k=3))

def make_password():
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=64))

def generate_signature(payload_str):
    return hmac.new(API_KEY, payload_str.encode(), hashlib.sha256).hexdigest()


# ==================== x.py FLOW — ALL ASYNC ====================
async def get_version_config(region=REGION):
    app_version = "1.132.9"
    if play_scraper:
        try:
            loop = asyncio.get_event_loop()
            res = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth').get('version'))
            app_version = res or app_version
        except Exception: pass
    lang = REGION_LANG.get(region.upper(), "en")
    url = (f"https://version.ggwhitehawk.com/live/ver.php?version={app_version}"
           f"&lang={lang}&device=android&channel=android&appstore=googleplay"
           f"&region={region.upper()}&whitelist_version=1.3.0&whitelist_sp_version=1.0.0")
    try:
        r = await client.get(url)
        j = r.json()
        server_url = j.get("server_url")
        remote_version = j.get("remote_version")
        latest_release_version = j.get("latest_release_version")
        gops = [u.strip() for u in j.get("gop_url","").split(";") if u.strip()]
        gop_1 = gops[0] if gops else "https://ffmconnect.ppmainecoonghj.com"
        if not server_url: return None
        return latest_release_version, remote_version, server_url, gop_1, app_version
    except Exception as e:
        return None


async def register_account(password, gop_url, app_version):
    """x.py's exact guest:register — uses GOP"""
    connector = aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())
    rp = {"app_id":100067,"client_type":2,"password":password,"source":2}
    payload = json.dumps(rp, separators=(',',':'))
    sig = generate_signature(payload)
    headers = {
        "User-Agent": f"GarenaMSDK/4.0.44(SM-E135F ;Android 14;en;GB;app {app_version} 2019118525;)",
        "Authorization": f"Signature {sig}",
        "Cookie": SharedCookie,
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"}
    try:
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.post(f"{gop_url}/api/v2/oauth/guest:register",
                              headers=headers, data=payload,
                              timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = json.loads(await resp.text())
                if data.get("code") == 0:
                    return data["data"]["uid"]
    except Exception as e:
        print(f"[REGISTER] {e}")
    return None


async def grant_token(uid, password, gop_url, app_version):
    """x.py's exact token:grant — uses GOP"""
    connector = aiohttp.TCPConnector(resolver=aiohttp.ThreadedResolver())
    gp = {"client_id":100067,"client_secret":HEX_KEY,"client_type":2,
          "device_id":f"02-{uuid.uuid4()}","password":password,
          "response_type":"token","uid":int(uid)}
    payload = json.dumps(gp, separators=(',',':'))
    sig = generate_signature(payload)
    headers = {
        "User-Agent": f"GarenaMSDK/4.0.44(SM-E135F ;Android 14;en;GB;app {app_version} 2019118525;)",
        "Authorization": f"Signature {sig}",
        "Accept": "application/json",
        "Content-Type": "application/json; charset=utf-8"}
    try:
        async with aiohttp.ClientSession(connector=connector) as s:
            async with s.post(f"{gop_url}/api/v2/oauth/guest/token:grant",
                              headers=headers, data=payload,
                              timeout=aiohttp.ClientTimeout(total=15)) as resp:
                data = json.loads(await resp.text())
                if data.get("code") == 0:
                    return data["data"]
    except Exception as e:
        print(f"[GRANT] {e}")
    return None


async def get_payload(access_token, open_id, platform, version, lang_code="en"):
    """x.py's exact payload"""
    device_id = f"Google|{uuid.uuid4()}"

    major_login = {
        "3": str(datetime.now())[:-7], "4": "free fire", "5": 1,
        "7": f"{version}",
        "8": "Android OS 14 / API-34 (UP1A.231005.007/E135FXXSEEZE2)",
        "9": "Handheld", "11": "CarrierDataNetwork",
        "12": 1672, "13": 750, "14": "338",
        "15": "ARMv7 VFPv3 NEON | 2002 | 8",
        "16": 3702, "17": "Mali-G52",
        "18": "OpenGL ES 3.2 v1.r38p1-01bet0-mbs2v41_0.6d20ec041e51b2f2d25dfc265586ebe8",
        "19": device_id, "20": "104.28.197.151", "21": lang_code,
        "22": f"{open_id}", "23": f"{platform}", "24": "Handheld",
        "25": "samsung SM-E135F", "26": REGION,
        "29": f"{access_token}", "30": 1, "42": "Cellular",
        "57": "7428b253defc164018c604a1ebbfebdf",
        "60": 52037, "61": 5355, "62": 3723, "63": 3,
        "64": 5483, "65": 52037, "66": 5483, "67": 52037,
        "73": 2,
        "74": "/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/lib/arm",
        "76": 1,
        "77": "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~yACsV8QOk9OexgajWQP30A==/com.dts.freefireth-Bi_wPVrrhYM2nYncc29q7Q==/base.apk",
        "78": 3, "79": 1, "81": "32", "83": "2019121229",
        "86": "OpenGLES2", "87": 8191, "88": int(platform),
        "92": 16091, "93": "android",
        "94": "KqsHT3Yeqo3RLRl8efNiL3aL/1SHwlSrtK0DwNAqdkNBQz70TeVy+icaIwuR3UK4b65Uf3IG5xBFEv0uu+jQZI+rOYCmNCsXjJT4QcZaYgoaaUGG",
        "95": 111107,
        "96": "{\"cur_rate\":null,\"support_etc2\":false}",
        "97": 1, "98": 1,
        "99": f"{platform}", "100": f"{platform}",
        "102": "4503454457550c0766",
        "104": 53792, "105": 1,
        "106": "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|6b2078db9d22dd98f8e9386a39af8462",
        "107": "c8e41b7a93f02d56e1a94c7b8203f5d1",
    }
    get_login_data = dict(major_login)
    get_login_data["90"] = "Khulna"
    get_login_data["91"] = "D"
    get_login_data["99"] = "0"
    get_login_data["103"] = 1

    proto1 = create_proto(major_login).hex()
    proto2 = create_proto(get_login_data).hex()
    return bytes.fromhex(encrypt_aes(proto1)), bytes.fromhex(encrypt_aes(proto2))


async def major_register(release_v, access_token, open_id, name, game_version,
                          login_url, lang_code="en"):
    """x.py's exact MajorRegister — login_url = HOST (game server)"""
    field14 = bytes(ord(c) ^ KEYSTREAM[i % 32] for i, c in enumerate(open_id))
    fields = {
        1:  name, 2:  access_token, 3:  open_id,
        5:  102000007, 6:  4, 7:  1, 13: 1,
        14: field14, 15: lang_code, 16: 2, 20: game_version, 21: 1, 22: GGRE_RAW,
    }
    proto = bytes(create_proto(fields))
    payload = AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(proto, 16))
    url = f"{login_url.rstrip('/')}/MajorRegister"
    hdrs = {
        "Accept": "*/*", "Authorization": "Bearer ",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": f"{release_v}",
        "User-Agent": UaUnity,
        "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
        "X-Unity-Version": uVer,
    }
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as s:
            async with s.post(url, headers=hdrs, data=payload, ssl=ssl_ctx) as resp:
                content = await resp.read()
                return resp.status, content
    except Exception as e:
        print(f"[MAJOR-REG] {e}")
        return None, None


async def major_login(payload, login_url, release_version):
    """x.py's EXACT major_login (with offset scan + score)"""
    url = f"{login_url.rstrip('/')}/MajorLogin"
    req_headers = {
        "Accept": "*/*", "Authorization": "Bearer ",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": f"{release_version}",
        "User-Agent": UaUnity,
        "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
        "X-Unity-Version": uVer,
    }
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            async with session.post(url, headers=req_headers, data=payload, ssl=ssl_context) as response:
                response_content = await response.read()
                print(f"[MAJOR-LOGIN] status={response.status} len={len(response_content)}")

                if response.status != 200:
                    preview = response_content[:120]
                    print(f"[MAJOR-LOGIN] HTTP {response.status}: {preview!r}")
                    return None
                if len(response_content) < 200:
                    print(f"[MAJOR-LOGIN] Short: {response_content.hex()}")
                    return None

                best = None
                best_score = -1
                best_off = 0
                offsets_to_try = [64, 0, 48, 32, 80, 16, 128, 8, 96, 60, 56, 40, 24, 20, 12, 4]

                for offset in offsets_to_try:
                    if offset >= len(response_content):
                        continue
                    cb = response_content[offset:]
                    cand = None
                    try:
                        cand = decode_protobuf_2(cb)
                        if cand:
                            cand = {str(k): {"data": v} for k, v in cand.items()}
                    except Exception:
                        cand = None
                    if not cand: continue

                    keys = set(cand.keys())
                    has_jwt = ("8" in keys) or (8 in keys)
                    has_url = ("10" in keys) or (10 in keys)
                    n = len(cand)
                    score = n + (100 if has_jwt else 0) + (50 if has_url else 0)

                    if score > best_score:
                        best = cand; best_score = score; best_off = offset
                    if has_jwt and has_url:
                        break

                if not best:
                    print(f"[MAJOR-LOGIN] Could not decode response")
                    return None

                if ("8" not in best) and (8 not in best):
                    print(f"[MAJOR-LOGIN] No JWT (field 8)")
                    return None

                best["__RAW_HEX__"] = response_content.hex()
                best["__OFFSET__"] = best_off
                return best
    except asyncio.TimeoutError:
        print("[MAJOR-LOGIN] TIMEOUT")
        return None
    except Exception as e:
        print(f"[MAJOR-LOGIN] {e}")
        traceback.print_exc()
        return None


async def choose_region(region, jwt_token, login_url, release_version):
    """x.py's EXACT ChooseRegion — login_url = HOST"""
    region_code = region.upper()
    url = f"{login_url.rstrip('/')}/ChooseRegion"
    proto = create_proto({1: region_code})
    payload = bytes.fromhex(encrypt_aes(proto.hex()))
    hdrs = {
        "Accept-Encoding": "gzip",
        "Authorization": f"Bearer {jwt_token}",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "ReleaseVersion": f"{release_version}",
        "User-Agent": UaUnity,
        "X-GA": "v1 1", "X-GA-SV": str(int(time.time())),
        "X-Unity-Version": uVer,
    }
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False
        ssl_ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as s:
            async with s.post(url, data=payload, headers=hdrs, ssl=ssl_ctx) as r:
                body = await r.read()
                print(f"[CHOOSE-REGION] {region} → HTTP {r.status} | body={body[:100]!r}")
                return r.status
    except Exception as e:
        print(f"[CHOOSE-REGION] {e}")
        return None


async def get_login_data(payload, jwt_token, server_url, release_version):
    """x.py's exact GetLoginData"""
    url = f"{server_url.rstrip('/')}/GetLoginData"
    hdrs = {"Accept":"*/*","Authorization":f"Bearer {jwt_token}",
        "Content-Type":"application/x-www-form-urlencoded",
        "ReleaseVersion":f"{release_version}",
        "User-Agent":UaUnity,"X-GA":"v1 1",
        "X-GA-SV":str(int(time.time())),"X-Unity-Version":uVer}
    try:
        ssl_ctx = ssl.create_default_context()
        ssl_ctx.check_hostname = False; ssl_ctx.verify_mode = ssl.CERT_NONE
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as s:
            async with s.post(url, headers=hdrs, data=payload, ssl=ssl_ctx) as r:
                if r.status != 200: return None
                content = await r.read()
                for off in [0,64,48,32,80,16,128,8,96]:
                    if off >= len(content): continue
                    try:
                        c = decode_protobuf_2(content[off:])
                        if c and len(c) >= 3: return c
                    except Exception: pass
                for off in [0,64,48,32,80]:
                    if off >= len(content): continue
                    c = decode_protobuf_2(content[off:])
                    if c and len(c) >= 3:
                        return {str(k):{"data":v} for k,v in c.items()}
        return None
    except Exception: return None


# ==================== MAIN GENERATOR (async) ====================
async def generate_one_async():
    """Full working guest gen flow using x.py's exact functions."""
    result = {
        "name": None, "uid": None, "password": None,
        "access_token": None, "open_id": None,
        "region": REGION, "in_game_uid": None, "level": None,
        "success": False, "error": None,
    }
    try:
        # 1) version config
        vc = await get_version_config(REGION)
        if not vc:
            result["error"] = "version config failed"
            return result
        release_v, remote_v, host, gop, app_version = vc
        game_version = remote_v or app_version
        if not host.endswith("/"): host += "/"

        # 2) register guest — GOP
        pwd = make_password()
        uid = await register_account(pwd, gop, app_version)
        if not uid:
            result["error"] = "register failed"
            return result
        result["uid"] = str(uid)
        result["password"] = pwd

        # 3) grant token — GOP
        tok = await grant_token(uid, pwd, gop, app_version)
        if not tok:
            result["error"] = "grant failed"
            return result
        open_id = tok["open_id"]
        access_token = tok["access_token"]
        platform = tok.get("platform", 4)
        result["access_token"] = access_token
        result["open_id"] = open_id

        # 4) payload
        major_payload, login_payload = await get_payload(
            access_token, open_id, platform, game_version, LANG
        )

        # 5) major register — HOST
        nickname = make_name()
        result["name"] = nickname
        status, content = await major_register(
            release_v, access_token, open_id,
            nickname, game_version, host, LANG
        )

        # 6) major login #1 — HOST
        res_json = None
        for attempt in range(3):
            mp, lp = await get_payload(access_token, open_id, platform, game_version, LANG)
            res_json = await major_login(mp, host, release_v)
            if res_json and (("8" in res_json) or (8 in res_json)):
                major_payload = mp; login_payload = lp; break
            res_json = None
            await asyncio.sleep(2.0)

        if not res_json:
            result["error"] = "MajorLogin #1 failed"
            return result

        def _gd(k):
            v = res_json.get(str(k))
            if isinstance(v, dict) and "data" in v: return v["data"]
            if isinstance(v, dict): return v.get("data")
            return v

        jwt_token = _gd(8)
        server_url_raw = _gd(10)
        acc_id_raw = _gd(1) or uid
        result["in_game_uid"] = str(acc_id_raw)

        # 7) ChooseRegion if server_url missing — HOST
        if not server_url_raw:
            cr = await choose_region(REGION, jwt_token, host, release_v)
            if cr == 200:
                await asyncio.sleep(2.0)
                # major login #2
                for attempt in range(3):
                    mp2, lp2 = await get_payload(access_token, open_id, platform, game_version, LANG)
                    res_json2 = await major_login(mp2, host, release_v)
                    if res_json2 and (("10" in res_json2) or (10 in res_json2)):
                        res_json = res_json2; login_payload = lp2
                        jwt_token = _gd(8)
                        server_url_raw = _gd(10)
                        break
                    await asyncio.sleep(2.0)

        # 8) get login data
        if server_url_raw:
            ld = await get_login_data(login_payload, jwt_token, server_url_raw, release_v)
            if ld:
                def _gf(f, d=None):
                    v = ld.get(str(f), {}).get("data")
                    return v if v is not None else d
                result["level"] = int(_gf(6, 1) or 1)

        result["success"] = (status == 200)
        if not result["success"] and content:
            body = content[:200].decode('utf-8', errors='ignore')
            result["error"] = f"MajorRegister HTTP {status}: {body}"

    except Exception as e:
        result["error"] = str(e)
        traceback.print_exc()

    return result


def generate_one():
    """Sync wrapper — creates fresh event loop per thread."""
    try:
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(generate_one_async())
        finally:
            try: loop.close()
            except Exception: pass
    except Exception as e:
        return {
            "name": None, "uid": None, "password": None,
            "access_token": None, "open_id": None,
            "region": REGION, "in_game_uid": None, "level": None,
            "success": False, "error": str(e),
        }


# ==================== FLASK APP ====================
app = Flask(__name__)

@app.errorhandler(Exception)
def _any_exc(e):
    return jsonify({"ok": False, "error": str(e)}), 500

@app.after_request
def _cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "app":         "MEHEDI GUEST GEN (x.py flow)",
        "region":      REGION,
        "name_prefix": NAME_PREFIX,
        "max_count":   MAX_COUNT,
        "flow":        "register → grant → MajorRegister → MajorLogin → ChooseRegion → GetLoginData",
        "endpoints": {
            "GET /gen?count=N": "Generate N guest accounts",
            "GET /gen1":        "Generate 1 guest account",
            "GET /health":      "Health check",
        },
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"ok": True, "region": REGION})


@app.route("/gen", methods=["GET"])
def gen():
    raw = request.args.get("count", "1")
    try: count = int(raw)
    except Exception:
        return jsonify({"ok": False, "error": f"invalid count: {raw}"}), 400

    count = max(1, min(count, MAX_COUNT))

    results = []
    with ThreadPoolExecutor(max_workers=Threads) as ex:
        futures = [ex.submit(generate_one) for _ in range(count)]
        for f in as_completed(futures):
            try: results.append(f.result())
            except Exception as e:
                results.append({"success": False, "error": str(e), "region": REGION})

    ok_count = sum(1 for r in results if r.get("success"))
    return jsonify({
        "ok":        True,
        "region":    REGION,
        "requested": count,
        "generated": ok_count,
        "failed":    count - ok_count,
        "accounts":  results,
    })


@app.route("/gen1", methods=["GET"])
def gen1():
    try:
        r = generate_one()
        return jsonify({"ok": r.get("success", False), "account": r})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ==================== MAIN ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=" * 55)
    print(f"  MEHEDI GUEST GEN — FLASK API (x.py flow)")
    print(f"  Region: {REGION}")
    print(f"  Name:   {NAME_PREFIX}xxx")
    print(f"  Port:   {port}")
    print("=" * 55)
    app.run(host="0.0.0.0", port=port, threaded=True)