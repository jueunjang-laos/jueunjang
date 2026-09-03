"""
포트폴리오 웹사이트 이미지 압축 스크립트.

index.html에서 실제로 쓰는 이미지 파일들을 대상으로:
- 가로/세로 최대 1600px로 축소 (이미 작으면 건드리지 않음)
- JPEG는 품질 80으로 재압축 (progressive + optimize)
- PNG는 무손실 최적화만 (투명도 보존 — award 배지용)
- 원본은 손실 없이 originals_backup/ 에 그대로 백업 후 덮어씀

사용법: python optimize_images.py
"""

from pathlib import Path
from PIL import Image
import shutil

ROOT = Path(__file__).parent
BACKUP_DIR = ROOT / "originals_backup"
MAX_DIMENSION = 1600
JPEG_QUALITY = 80

# index.html에서 <img src="./...">로 참조하는 파일들
TARGET_FILES = [
    "clay_dogs_collection_main.jpg",
    "clay_dogs_collection_full.jpg",
    "cosplay_mask_goggles.jpg",
    "paper_mask_01.jpg",
    "paper_mask_02.jpg",
    "craft_cctv_model.jpg",
    "aquarium_visit_2025_observation_01.jpeg",
    "aquarium_visit_2025_observation_02.jpeg",
    "aquarium_visit_2025_observation_03.jpeg",
    "aquarium_visit_2025_observation_04.jpeg",
    "aquarium_visit_2025_observation_05.jpeg",
    "aquarium_visit_2025_observation_06.jpeg",
    "aquarium_visit_2025_observation_07.jpeg",
    "aquarium_visit_2025_observation_08.jpeg",
    "aquarium_visit_2025_observation_09.jpeg",
    "marine_sketch_sea_animals.jpg",
    "scientific_illustration_bird_morphology.jpg",
    "zoological_sketch_animal_anatomy_01.jpg",
    "zoo_animal_anatomy_study_01.jpg",
    "zoo_animal_anatomy_study_06.jpg",
    "20260522_dindi_s8_classroom.jpg",
    "20260522_dindi_s8_lao_board.jpg",
    "20260522_dindi_s8_lesson_plan.jpg",
    "20260522_dindi_s8_collab.jpg",
    "20260522_dindi_s8_butterfly.jpg",
    "hero.jpg",
    "2023_xk_mural_jueun.jpg",
    "2023_xk_mural_jueun2.jpg",
    "2023_xk_school_sign.jpg",
    "award_01.png",
    "award_02.png",
    "award_03.png",
    "award_04.png",
]


def human(n: int) -> str:
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f}{unit}"
        n /= 1024
    return f"{n:.1f}GB"


def optimize(path: Path) -> tuple[int, int]:
    import io
    from PIL import ImageOps

    before = path.stat().st_size

    with Image.open(path) as img:
        # EXIF 회전 정보 반영 (스마트폰 사진이 옆으로 눕는 문제 방지)
        img = ImageOps.exif_transpose(img)

        if img.width > MAX_DIMENSION or img.height > MAX_DIMENSION:
            img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

        suffix = path.suffix.lower()
        buf = io.BytesIO()
        if suffix in (".jpg", ".jpeg"):
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
        elif suffix == ".png":
            img.save(buf, "PNG", optimize=True)
        else:
            img.save(buf, img.format)

    # 재압축 결과가 원본보다 크면(이미 작은 파일 등) 원본을 그대로 유지
    if buf.tell() < before:
        path.write_bytes(buf.getvalue())

    after = path.stat().st_size
    return before, after


def main():
    BACKUP_DIR.mkdir(exist_ok=True)

    rows = []
    total_before = total_after = 0

    for name in TARGET_FILES:
        src = ROOT / name
        if not src.exists():
            print(f"  (건너뜀 — 파일 없음: {name})")
            continue

        backup_path = BACKUP_DIR / name
        if not backup_path.exists():
            shutil.copy2(src, backup_path)

        before, after = optimize(src)
        total_before += before
        total_after += after
        rows.append((name, before, after))

    print(f"\n{'파일':45} {'이전':>10} {'이후':>10} {'절감':>8}")
    print("-" * 78)
    for name, before, after in rows:
        pct = (1 - after / before) * 100 if before else 0
        print(f"{name:45} {human(before):>10} {human(after):>10} {pct:>6.1f}%")

    print("-" * 78)
    total_pct = (1 - total_after / total_before) * 100 if total_before else 0
    print(f"{'합계':45} {human(total_before):>10} {human(total_after):>10} {total_pct:>6.1f}%")
    print(f"\n원본은 {BACKUP_DIR} 에 백업되어 있습니다 (git에는 커밋되지 않음).")


if __name__ == "__main__":
    main()
