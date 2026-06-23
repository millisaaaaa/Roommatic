# /home/pi/Roommatic/scripts/vision/people_counter.py

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import cv2
from ultralytics import YOLO
from picamera2 import Picamera2


class PeopleCounter:
    """
    Roommatic 人數辨識模組

    功能：
    1. 使用 Pi Camera 擷取影像
    2. 使用 YOLO 偵測 person 類別
    3. 輸出人數到 count.json
    4. 測試階段可輸出框選圖 boxed_latest.png
    5. 正式系統只需讀取 count.json，不需保存原始影像

    注意：
    - boxed image 主要用於測試與簡報展示。
    - 系統正式運作時，資料庫只需保存 people_num，不保存原始影像。
    """

    def __init__(
        self,
        model_name: str = "yolov8n.pt",
        conf: float = 0.30,
        iou: float = 0.45,
        width: int = 640,
        height: int = 480,
        base_dir: Optional[str | Path] = None,
        keep_images: int = 10,
        save_boxed_image: bool = True,
        enhance_low_light: bool = True,
        min_box_area: int = 300,
    ):
        """
        參數說明：
        model_name:
            YOLO 模型名稱。
            yolov8n.pt 速度快，適合 Raspberry Pi。
            yolov8s.pt 準確率通常較好，但較慢。

        conf:
            confidence threshold。
            原本 0.4 比較保守，低光源與遮擋容易漏判。
            這裡改成 0.30，兼顧穩定與漏判改善。

        iou:
            NMS IoU threshold。
            多人靠近或重疊時，0.45 通常比 0.5 稍微寬鬆。

        save_boxed_image:
            True：儲存框選圖，適合測試與簡報。
            False：正式部署時可關閉，降低隱私疑慮。

        enhance_low_light:
            True：對低光源影像做 CLAHE 對比增強。

        min_box_area:
            過小框可能是誤判，可過濾掉。
            若拍遠距離教室，人很小，可以降低此值。
        """

        self.model_name = model_name
        self.conf = conf
        self.iou = iou
        self.width = width
        self.height = height
        self.keep_images = keep_images
        self.save_boxed_image = save_boxed_image
        self.enhance_low_light = enhance_low_light
        self.min_box_area = min_box_area

        if base_dir is None:
            self.base_dir = Path.home() / "Roommatic" / "scripts" / "vision"
        else:
            self.base_dir = Path(base_dir)

        self.images_dir = self.base_dir / "images"
        self.images_dir.mkdir(parents=True, exist_ok=True)

        self.count_json = self.base_dir / "count.json"
        self.boxed_latest = self.base_dir / "boxed_latest.png"

        print(f"[PeopleCounter] Loading model: {self.model_name}")
        self.model = YOLO(self.model_name)

        print("[PeopleCounter] Starting camera...")
        self.cam = Picamera2()
        self.cam.configure(
            self.cam.create_still_configuration(
                main={"size": (self.width, self.height)}
            )
        )
        self.cam.start()

    # =====================================================
    # 低光源影像增強
    # =====================================================
    def _enhance_image_for_low_light(self, img_bgr):
        """
        使用 CLAHE 提升暗部對比。
        適合低光源、背光、室內昏暗測試。

        不會改變原始儲存邏輯，只是讓 YOLO 推論時的輸入更清楚。
        """
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(
            clipLimit=2.0,
            tileGridSize=(8, 8)
        )
        enhanced_l = clahe.apply(l_channel)

        enhanced_lab = cv2.merge((enhanced_l, a_channel, b_channel))
        enhanced_bgr = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

        return enhanced_bgr

    # =====================================================
    # 寫入 count.json
    # =====================================================
    def _write_count_json(
        self,
        ts: str,
        count: int,
        latest_image_path: Optional[str],
        raw_count: int,
        filtered_count: int,
    ):
        payload = {
            "timestamp": ts,
            "count": count,
            "raw_count": raw_count,
            "filtered_count": filtered_count,
            "model": self.model_name,
            "conf": self.conf,
            "iou": self.iou,
            "resolution": [self.width, self.height],
            "enhance_low_light": self.enhance_low_light,
            "save_boxed_image": self.save_boxed_image,
            "privacy_note": "Only people count is required for database storage. Boxed images are for testing/presentation validation only.",
            "latest_boxed_image": latest_image_path,
        }

        self.count_json.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # =====================================================
    # 清除舊測試圖片
    # =====================================================
    def _cleanup_old_images(self):
        image_files = sorted(self.images_dir.glob("boxed_*.png"))

        if len(image_files) > self.keep_images:
            old_files = image_files[: len(image_files) - self.keep_images]

            for f in old_files:
                try:
                    f.unlink()
                except Exception as e:
                    print(f"[PeopleCounter] Failed to delete old image {f}: {e}")

    # =====================================================
    # 畫框與總人數
    # =====================================================
    def _draw_results(self, img_bgr, detections: list[dict], count: int, ts: str):
        boxed = img_bgr.copy()

        for det in detections:
            x1 = det["x1"]
            y1 = det["y1"]
            x2 = det["x2"]
            y2 = det["y2"]
            conf = det["conf"]

            cv2.rectangle(
                boxed,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )

            label = f"Person {conf:.2f}"
            cv2.putText(
                boxed,
                label,
                (x1, max(20, y1 - 5)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                1,
                cv2.LINE_AA
            )

        # 左上角總人數，簡報截圖會更清楚
        cv2.rectangle(
            boxed,
            (10, 10),
            (310, 80),
            (0, 0, 0),
            -1
        )

        cv2.putText(
            boxed,
            f"People Count: {count}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 255, 0),
            2,
            cv2.LINE_AA
        )

        cv2.putText(
            boxed,
            ts,
            (20, 68),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (200, 200, 200),
            1,
            cv2.LINE_AA
        )

        return boxed

    # =====================================================
    # 單次偵測
    # =====================================================
    def run_once(self):
        now = datetime.now()
        ts_file = now.strftime("%Y%m%d_%H%M%S")
        ts = now.strftime("%Y-%m-%d %H:%M:%S")

        # 1. 擷取影像
        frame = self.cam.capture_array()
        img_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        # 2. 低光源增強，只用於推論
        if self.enhance_low_light:
            infer_img = self._enhance_image_for_low_light(img_bgr)
        else:
            infer_img = img_bgr

        # 3. YOLO 推論，只偵測 person 類別 classes=[0]
        results = self.model.predict(
            source=infer_img,
            conf=self.conf,
            iou=self.iou,
            classes=[0],
            verbose=False
        )

        # 4. 解析偵測框
        raw_count = 0
        detections: list[dict] = []

        for r in results:
            for box in r.boxes:
                raw_count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])
                c = float(box.conf[0])

                box_area = max(0, x2 - x1) * max(0, y2 - y1)

                # 過濾太小的框，降低誤判
                if box_area < self.min_box_area:
                    continue

                detections.append(
                    {
                        "x1": x1,
                        "y1": y1,
                        "x2": x2,
                        "y2": y2,
                        "conf": c,
                        "area": box_area,
                    }
                )

        filtered_count = len(detections)
        count = filtered_count

        latest_image_path = None
        history_img = None

        # 5. 測試階段輸出框選圖
        if self.save_boxed_image:
            boxed = self._draw_results(
                img_bgr=img_bgr,
                detections=detections,
                count=count,
                ts=ts
            )

            cv2.imwrite(str(self.boxed_latest), boxed)

            history_img = self.images_dir / f"boxed_{ts_file}.png"
            cv2.imwrite(str(history_img), boxed)

            latest_image_path = str(self.boxed_latest)

            self._cleanup_old_images()

        # 6. 寫入 count.json
        self._write_count_json(
            ts=ts,
            count=count,
            latest_image_path=latest_image_path,
            raw_count=raw_count,
            filtered_count=filtered_count,
        )

        print(
            f"[{ts}] people_count={count}, "
            f"raw_count={raw_count}, "
            f"conf={self.conf}, iou={self.iou}, "
            f"low_light_enhance={self.enhance_low_light}"
        )

        return {
            "timestamp": ts,
            "count": count,
            "raw_count": raw_count,
            "filtered_count": filtered_count,
            "boxed_latest": str(self.boxed_latest) if self.save_boxed_image else None,
            "history_image": str(history_img) if history_img else None,
            "conf": self.conf,
            "iou": self.iou,
            "enhance_low_light": self.enhance_low_light,
        }

    # =====================================================
    # 關閉相機
    # =====================================================
    def close(self):
        try:
            self.cam.close()
        except Exception as e:
            print(f"[PeopleCounter] Camera close error: {e}")


# =========================================================
# 給 main.py 用的輕量函式
# =========================================================
def get_people_count() -> int:
    """
    不重新開相機、不重跑 YOLO。
    直接讀最近一次 count.json 的結果。

    main.py 建議使用這個函式，避免每次控制週期都重新初始化相機與模型。
    """
    count_json = Path.home() / "Roommatic" / "scripts" / "vision" / "count.json"

    if not count_json.exists():
        return 0

    try:
        data = json.loads(count_json.read_text(encoding="utf-8"))
        return int(data.get("count", 0))
    except Exception as e:
        print(f"get_people_count() error: {e}")
        return 0


def run_and_get_people_count() -> int:
    """
    真的跑一次相機 + YOLO，回傳最新人數。

    使用較寬的 16:9 畫面，讓 boxed_latest.png 的取景範圍
    更接近 rpicam-hello 預覽畫面。
    """
    counter = PeopleCounter(
        model_name="yolov8n.pt",
        conf=0.30,
        iou=0.45,
        width=1024,
        height=576,
        keep_images=10,
        save_boxed_image=True,
        enhance_low_light=True,
        min_box_area=150,
    )

    try:
        result = counter.run_once()
        return int(result["count"])
    finally:
        counter.close()


# =========================================================
# 測試用入口
# =========================================================
if __name__ == "__main__":
    counter = PeopleCounter(
        model_name="yolov8n.pt",
        conf=0.30,
        iou=0.45,
        width=640,
        height=480,
        keep_images=10,
        save_boxed_image=True,
        enhance_low_light=True,
        min_box_area=300,
    )

    try:
        result = counter.run_once()
        print(result)
    finally:
        counter.close()