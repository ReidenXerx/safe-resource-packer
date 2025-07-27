import os
import argparse
import hashlib
import shutil
from datetime import datetime
import sys

LOGS = []
SKIPPED = []

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGS.append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

def print_progress(current, total, packed, loose, skipped):
    bar_len = 40
    filled_len = int(round(bar_len * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write(f"\r[{bar}] {percents}% | Packed: {packed} | Loose: {loose} | Skipped: {skipped} ")
    sys.stdout.flush()

def write_log_file(path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(LOGS))
        if SKIPPED:
            f.write('\n\n[SKIPPED FILES]\n')
            f.write('\n'.join(SKIPPED))
        log(f"Log written to {path}")
    except Exception as e:
        print(f"Failed to write log file: {e}")

def hash_file(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except Exception as e:
        SKIPPED.append(f"[HASH FAIL] {path}: {e}")
        return None

def collect_hashes(base_dir):
    hash_map = {}
    total_count = 0
    for root, _, files in os.walk(base_dir):
        for file in files:
            total_count += 1
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):
                file_hash = hash_file(full_path)
                if file_hash:
                    hash_map[file_hash] = full_path
    return hash_map, total_count

def copy_file(src, rel_path, base_out):
    try:
        dest_path = os.path.join(base_out, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src, dest_path)
        return True
    except Exception as e:
        SKIPPED.append(f"[COPY FAIL] {rel_path}: {e}")
        return False

def classify_by_hash(generated_hashes, source_hashes, out_pack, out_loose):
    pack_count = 0
    loose_count = 0
    current = 0
    total = len(generated_hashes)
    for h, gen_path in generated_hashes.items():
        rel_path = os.path.basename(gen_path)
        current += 1
        if h in source_hashes:
            if copy_file(gen_path, rel_path, out_loose):
                loose_count += 1
        else:
            if copy_file(gen_path, rel_path, out_pack):
                pack_count += 1
        print_progress(current, total, pack_count, loose_count, len(SKIPPED))
    print()  # new line after progress bar
    return pack_count, loose_count

def main():
    parser = argparse.ArgumentParser(description="🧠 Safe Resource Packer for Skyrim (Hash Mode)")
    parser.add_argument('--source', required=True, help='Path to original loose resources folder or Vortex staging')
    parser.add_argument('--generated', required=True, help='Path to generated resources folder (e.g. BodySlide output)')
    parser.add_argument('--output-pack', required=True, help='Path to copy safe-to-pack files')
    parser.add_argument('--output-loose', required=True, help='Path to copy override files (should stay loose)')
    parser.add_argument('--log', default='safe_resource_packer.log', help='Path to log output file (include .log)')

    args = parser.parse_args()

    try:
        log(f"Scanning source directory: {args.source}")
        source_hashes, source_total = collect_hashes(args.source)
        log(f"Hashed {source_total} files from source")

        log(f"Scanning generated directory: {args.generated}")
        generated_hashes, generated_total = collect_hashes(args.generated)
        log(f"Hashed {generated_total} files from generated folder")

        log(f"Classifying generated files by content hash...")
        pack_count, loose_count = classify_by_hash(generated_hashes, source_hashes, args.output_pack, args.output_loose)

        log("\n===== SUMMARY =====")
        log(f"Generated files total: {generated_total}")
        log(f"Classified for packing (unique): {pack_count}")
        log(f"Classified for loose (overrides): {loose_count}")
        log(f"Skipped or errored: {len(SKIPPED)}")

        if SKIPPED:
            log("\n⚠️  Some files were skipped due to errors:")
            for s in SKIPPED:
                log(s)

    except Exception as e:
        log(f"Fatal error: {e}")
    finally:
        write_log_file(args.log)

if __name__ == '__main__':
    main()
