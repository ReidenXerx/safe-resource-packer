import os
import argparse
import hashlib
import shutil
from datetime import datetime

LOGS = []

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGS.append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

def write_log_file(path):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(LOGS))
        log(f"Log written to {path}")
    except Exception as e:
        log(f"Error writing log file: {e}")

def hash_file(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except Exception as e:
        log(f"Error hashing file {path}: {e}")
        return None

def collect_files(base_dir):
    file_map = {}
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.nif'):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, base_dir).lower()
                file_map[rel_path] = full_path
    return file_map

def copy_file(src, rel_path, base_out):
    try:
        dest_path = os.path.join(base_out, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src, dest_path)
        return True
    except Exception as e:
        log(f"Error copying {src} to {base_out}: {e}")
        return False

def split_and_copy(source_map, exclude_map, out_pack, out_loose):
    pack_count = 0
    loose_count = 0

    for rel_path, src_path in source_map.items():
        if rel_path in exclude_map:
            if copy_file(src_path, rel_path, out_loose):
                log(f"[LOOSE] {rel_path} (override match)")
                loose_count += 1
        else:
            if copy_file(src_path, rel_path, out_pack):
                log(f"[PACK]  {rel_path}")
                pack_count += 1

    return pack_count, loose_count

def main():
    parser = argparse.ArgumentParser(description="🧠 Safe Resource Packer for Skyrim")
    parser.add_argument('--source', required=True, help='Path to original loose meshes folder')
    parser.add_argument('--exclude', required=True, help='Path to override folder (e.g. BodySlide output)')
    parser.add_argument('--output-pack', required=True, help='Path to copy safe-to-pack files')
    parser.add_argument('--output-loose', required=True, help='Path to copy override files (should stay loose)')
    parser.add_argument('--log', default='safe_resource_packer.log', help='Path to log output file (include .log)')

    args = parser.parse_args()

    try:
        log(f"Scanning source: {args.source}")
        source_map = collect_files(args.source)
        log(f"Found {len(source_map)} files in source")

        log(f"Scanning exclude: {args.exclude}")
        exclude_map = collect_files(args.exclude)
        log(f"Found {len(exclude_map)} files in exclude")

        log(f"Copying files...")
        pack_count, loose_count = split_and_copy(source_map, exclude_map, args.output_pack, args.output_loose)

        log(f"Finished.")
        log(f"Total safe-to-pack: {pack_count}")
        log(f"Total to remain loose: {loose_count}")

    except Exception as e:
        log(f"Fatal error: {e}")
    finally:
        write_log_file(args.log)

if __name__ == '__main__':
    main()
