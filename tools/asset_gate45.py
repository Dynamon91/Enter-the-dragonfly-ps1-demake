"""Fail-closed intake audit for local source-first ETD restoration assets.
Not a converter, emulator test, or license checker. WAV is an intermediate.
"""
import argparse, hashlib, json, re, struct, wave
from pathlib import Path

RELEASED = {"etd_retail"}
EXPANDED = RELEASED | {"etd_prototype", "etd_unused_music", "spyro_ps1", "spyro2_ps1", "fan_original"}
MUSIC = {"etd_retail", "etd_unused_music", "fan_original"}
REVIEWS = {"model": ("silhouette", "uv", "animation"), "scene": ("layout", "collision", "portal"), "music": ("track_identity", "loop_listen", "stream_test"), "sfx": ("identity", "playback")}


def sha256(path):
    with path.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def resolve_file(root, rel):
    if not isinstance(rel, str) or not rel or Path(rel).is_absolute():
        raise ValueError('expected a relative file path')
    p = (root / rel).resolve()
    if not p.is_relative_to(root) or not p.is_file():
        raise ValueError('file missing or outside local asset root')
    return p


def audit_wav(path, loop=None):
    """16-bit PCM intermediate: bound memory per read; loop indices in frames."""
    errors, warnings = [], []
    with wave.open(str(path), 'rb') as w:
        n, rate, ch = w.getnframes(), w.getframerate(), w.getnchannels()
        if w.getsampwidth() != 2 or ch not in (1, 2) or not 8000 <= rate <= 48000 or n <= 0:
            return ['expected nonempty 16-bit PCM, mono/stereo, 8–48 kHz'], warnings
        peak = actual = clipped = 0
        while actual < n:
            b = w.readframes(min(8192, n - actual))
            if not b or len(b) % (2 * ch):
                return ['truncated PCM data'], warnings
            actual += len(b) // (2 * ch)
            for (sample,) in struct.iter_unpack('<h', b):
                peak = max(peak, abs(sample))
                clipped += sample in (-32768, 32767)
        if peak == 0:
            errors.append('entire audio file is silent')
        if clipped:
            warnings.append(f'{clipped} full-scale samples; listen for clipping')
        if loop is not None:
            if not (isinstance(loop, list) and len(loop) == 2 and all(type(x) is int for x in loop) and 0 <= loop[0] < loop[1] <= n):
                errors.append('invalid loop [start, end-exclusive] in sample frames')
            else:
                w.setpos(loop[0]); first = struct.unpack('<' + 'h'*ch, w.readframes(1))
                w.setpos(loop[1]-1); last = struct.unpack('<' + 'h'*ch, w.readframes(1))
                jump = max(abs(a-b) for a,b in zip(first,last))
                if jump > 2048:
                    warnings.append(f'loop endpoint jump {jump}/32768; listen for a click')
    return errors, warnings


def inventory():
    result = {}
    for n in range(30):
        scope = 'released' if n < 9 else 'expanded'
        for kind in ('scene', 'music'):
            result[f'{kind}.level.{n:02}'] = (kind, scope)
    for n, name in enumerate(('crush', 'gulp', 'ripto', 'gnasty', 'alliance')):
        scope = 'released' if n == 2 else 'expanded'
        for kind in ('scene', 'music'):
            result[f'{kind}.boss.{name}'] = (kind, scope)
    for name in ('spyro', 'sparx', 'dragonfly', 'ripto', 'npc_bank', 'enemy_bank'):
        result[f'model.{name}'] = ('model', 'released')
    for name in ('crush', 'gulp', 'gnasty'):
        result[f'model.{name}'] = ('model', 'expanded')
    result['sfx.retail_bank'] = ('sfx', 'released')
    return result


def audit(manifest, root, mode):
    root = Path(root).resolve()
    errors, warnings, seen = [], [], set()
    expected = inventory()
    records = manifest.get('assets')
    if not isinstance(records, list) or not records:
        return ['asset inventory missing or empty'], []
    for a in records:
        if not isinstance(a, dict):
            errors.append('non-object asset record'); continue
        key, kind, scope = a.get('id'), a.get('kind'), a.get('scope')
        def fail(msg): errors.append(f'{key}: {msg}')
        if not isinstance(key, str) or not key or key in seen:
            fail('missing or duplicate id'); continue
        seen.add(key)
        if kind not in REVIEWS or scope not in ('released', 'expanded'):
            fail('unknown kind or scope'); continue
        if key in expected and expected[key] != (kind, scope):
            fail('kind/scope differs from required inventory'); continue
        if mode == 'classic' and scope == 'expanded': continue
        if a.get('status') != 'verified':
            fail('not verified; unavailable for release'); continue
        source = a.get('source')
        allowed = RELEASED if scope == 'released' else EXPANDED
        if source not in allowed or (kind == 'music' and source not in MUSIC):
            fail('source violates restoration policy'); continue
        if not isinstance(a.get('source_ref'), str) or not a['source_ref'].strip():
            fail('missing source resource/disc or composition reference')
        for role in ('input', 'output'):
            try:
                p = resolve_file(root, a.get(role+'_path'))
                digest = a.get(role+'_sha256', '')
                if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest) or sha256(p) != digest:
                    fail(role+' SHA256 mismatch')
                if role == 'input' and kind in ('music', 'sfx'):
                    loop = a.get('loop_frames')
                    if kind == 'music' and loop is None: fail('missing explicit music loop')
                    es, ws = audit_wav(p, loop)
                    for e in es: fail(e)
                    warnings.extend(f'{key}: {w}' for w in ws)
            except (OSError, ValueError, EOFError, wave.Error, struct.error) as e:
                fail(f'{role}: {e}')
        review = a.get('reviews', {})
        if not isinstance(review, dict) or any(review.get(r) is not True for r in REVIEWS[kind]):
            fail('required human/runtime review flags incomplete')
    for key, (_, scope) in expected.items():
        if key not in seen and (mode == 'expanded' or scope == 'released'):
            errors.append(f'{key}: required inventory entry absent')
    return errors, warnings


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('manifest', type=Path); p.add_argument('asset_root', type=Path)
    p.add_argument('--mode', choices=('classic','expanded'), required=True)
    args = p.parse_args()
    try:
        m = json.loads(args.manifest.read_text())
        if not isinstance(m, dict): raise ValueError('expected manifest object')
        errors, warnings = audit(m, args.asset_root, args.mode)
    except (ValueError, OSError) as e:
        errors, warnings = [str(e)], []
    for w in warnings: print('WARN:', w)
    for e in errors: print('BLOCK:', e)
    print(f'{len(errors)} blocking findings; {len(warnings)} warnings. ' + ('RELEASE INTAKE BLOCKED' if errors else 'INTAKE CHECK PASSED (not gameplay certification)'))
    return int(bool(errors))

if __name__ == '__main__': raise SystemExit(main())
