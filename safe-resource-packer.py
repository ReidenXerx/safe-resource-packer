import os
import argparse
import shutil
import hashlib
from datetime import datetime
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

LOGS = []
SKIPPED = []
LOCK = threading.Lock()

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    LOGS.append(f"[{timestamp}] {message}")
    print(f"[{timestamp}] {message}")

def print_progress(current, total, stage, extra=""):
    bar_len = 40
    filled_len = int(round(bar_len * current / float(total)))
    percents = round(100.0 * current / float(total), 1)
    bar = '=' * filled_len + ' ' * (bar_len - filled_len)
    sys.stdout.write(f"\r[{bar}] {percents}% | {stage} {extra}   ")
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

def copy_folder_to_temp(source):
    temp_dir = tempfile.mkdtemp()
    log(f"Copying source to temp directory: {temp_dir}")
    shutil.copytree(source, os.path.join(temp_dir, 'source'), dirs_exist_ok=True)
    return os.path.join(temp_dir, 'source'), temp_dir

def file_hash(path):
    try:
        with open(path, 'rb') as f:
            return hashlib.sha1(f.read()).hexdigest()
    except Exception as e:
        with LOCK:
            SKIPPED.append(f"[HASH FAIL] {path}: {e}")
        return None
def classify_by_path(source_root, generated_root, out_pack, out_loose, threads=8):
    def find_file_case_insensitive(root, rel_path):
        parts = rel_path.split(os.sep)
        current = root
        for part in parts:
            try:
                entries = os.listdir(current)
            except FileNotFoundError:
                return None
            match = next((e for e in entries if e.lower() == part.lower()), None)
            if not match:
                return None
            current = os.path.join(current, match)
        return current if os.path.isfile(current) else None

    all_gen_files = []
    for root, _, files in os.walk(generated_root):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, generated_root)
            all_gen_files.append((full_path, rel_path))

    total = len(all_gen_files)
    current = 0
    pack_count, loose_count, skip_count = 0, 0, 0

    def process_file(gen_path, rel_path):
        src_path = os.path.join(source_root, rel_path)

        # если файл есть по нормальному пути
        if os.path.exists(src_path):
            gen_hash = file_hash(gen_path)
            src_hash = file_hash(src_path)
            if gen_hash == src_hash:
                return 'skip', rel_path
            elif copy_file(gen_path, rel_path, out_loose):
                return 'loose', rel_path

        else:
            # ищем регистронезависимо
            alt_src_path = find_file_case_insensitive(source_root, rel_path)
            if alt_src_path:
                gen_hash = file_hash(gen_path)
                src_hash = file_hash(alt_src_path)
                if gen_hash == src_hash:
                    return 'skip', rel_path
                elif copy_file(gen_path, rel_path, out_loose):
                    return 'loose', rel_path

        # если ничего не найдено — pack
        if copy_file(gen_path, rel_path, out_pack):
            return 'pack', rel_path
        return 'fail', rel_path

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(process_file, gp, rp) for gp, rp in all_gen_files]
        for future in as_completed(futures):
            result, path = future.result()
            current += 1
            print_progress(current, total, "Classifying")
            if result == 'loose':
                loose_count += 1
            elif result == 'pack':
                pack_count += 1
            elif result == 'skip':
                skip_count += 1
    print()
    return pack_count, loose_count, skip_count

def copy_file(src, rel_path, base_out):
    try:
        dest_path = os.path.join(base_out, rel_path)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src, dest_path)
        return True
    except Exception as e:
        with LOCK:
            SKIPPED.append(f"[COPY FAIL] {rel_path}: {e}")
        return False

def main():
    temp_dir = None
    parser = argparse.ArgumentParser(description="🧠 Safe Resource Packer for Skyrim (Path Mode)")
    parser.add_argument('--source', required=True, help='Path to final Data folder or Vortex deployed repo')
    parser.add_argument('--generated', required=True, help='Path to generated resources folder (e.g. BodySlide output)')
    parser.add_argument('--output-pack', required=True, help='Path to copy safe-to-pack files')
    parser.add_argument('--output-loose', required=True, help='Path to copy override files (should stay loose)')
    parser.add_argument('--log', default='safe_resource_packer.log', help='Path to log output file (include .log)')
    parser.add_argument('--threads', type=int, default=8, help='Number of threads to use')

    args = parser.parse_args()

    try:
        real_source, temp_dir = copy_folder_to_temp(args.source)

        log(f"Classifying generated files by path override logic...")
        pack_count, loose_count, skip_count = classify_by_path(
            real_source, args.generated, args.output_pack, args.output_loose, args.threads
        )

        log("\n===== SUMMARY =====")
        log(f"Classified for packing (new): {pack_count}")
        log(f"Classified for loose (override): {loose_count}")
        log(f"Skipped (identical): {skip_count}")
        log(f"Skipped or errored: {len(SKIPPED)}")

        if SKIPPED:
            log("\n⚠️  Some files were skipped due to errors:")
            for s in SKIPPED:
                log(s)

    except KeyboardInterrupt:
        log("Process interrupted by user (Ctrl+C)")
    except Exception as e:
        log(f"Fatal error: {e}")
    finally:
        write_log_file(args.log)
        if temp_dir:
            try:
                shutil.rmtree(temp_dir)
                log(f"Cleaned up temp directory: {temp_dir}")
            except Exception as e:
                log(f"Failed to clean temp directory: {e}")

if __name__ == '__main__':
    main()
