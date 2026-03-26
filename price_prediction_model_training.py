

import os
import sys
import json
from pathlib import Path

import boto3
import numpy as np
import pandas as pd
import sagemaker
from sklearn.model_selection import train_test_split
from sagemaker import image_uris
from sagemaker.estimator import Estimator
from sagemaker.inputs import TrainingInput

# =========================
# 1) Cấu hình cơ bản
# =========================
LOCAL_CSV = "cardata.csv"
TARGET_COL = "Selling_Price"
S3_PREFIX = "car-price-xgboost"
INSTANCE_TYPE = "ml.m5.large"
INSTANCE_COUNT = 1
XGBOOST_VERSION = "1.7-1"

RANDOM_STATE = 42
CURRENT_YEAR = 2026

REQUIRED_COLUMNS = [
    "Year",
    "Selling_Price",
    "Present_Price",
    "Kms_Driven",
    "Fuel_Type",
    "Seller_Type",
    "Transmission",
    "Owner",
]


# =========================
# 2) Hàm tiện ích
# =========================
def log(msg: str) -> None:
    print(f"[INFO] {msg}")


def fail(msg: str) -> None:
    print(f"[ERROR] {msg}", file=sys.stderr)
    sys.exit(1)


def check_input_file(path: str) -> None:
    if not Path(path).exists():
        fail(f"Không tìm thấy file dữ liệu: {path}")


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tiền xử lý tối giản cho bài toán giá xe.
    """
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        fail(f"Thiếu các cột bắt buộc trong CSV: {missing}")

    # Giữ đúng các cột cần dùng
    df = df[REQUIRED_COLUMNS].copy()

    # Loại bỏ missing trước khi map
    df = df.dropna().reset_index(drop=True)

    # Tạo tuổi xe
    df["Car_Age"] = CURRENT_YEAR - df["Year"]
    df.drop(columns=["Year"], inplace=True)

    # Encode category
    fuel_map = {"Petrol": 0, "Diesel": 1, "CNG": 2}
    seller_map = {"Dealer": 0, "Individual": 1}
    transmission_map = {"Manual": 0, "Automatic": 1}

    df["Fuel_Type"] = df["Fuel_Type"].map(fuel_map)
    df["Seller_Type"] = df["Seller_Type"].map(seller_map)
    df["Transmission"] = df["Transmission"].map(transmission_map)

    # Loại bỏ dòng có category ngoài mapping
    df = df.dropna().reset_index(drop=True)

    # Ép kiểu số
    numeric_cols = [
        "Selling_Price",
        "Present_Price",
        "Kms_Driven",
        "Fuel_Type",
        "Seller_Type",
        "Transmission",
        "Owner",
        "Car_Age",
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna().reset_index(drop=True)

    # Loại bỏ giá trị bất thường cơ bản
    df = df[df["Car_Age"] >= 0].reset_index(drop=True)

    if df.empty:
        fail("Dữ liệu sau tiền xử lý rỗng.")

    return df


def split_data(df: pd.DataFrame):
    train_df, test_df = train_test_split(
        df, test_size=0.2, random_state=RANDOM_STATE
    )
    train_df, val_df = train_test_split(
        train_df, test_size=0.2, random_state=RANDOM_STATE
    )
    return train_df, val_df, test_df


def reorder_for_sagemaker(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    feature_cols = [c for c in df.columns if c != target_col]
    return df[[target_col] + feature_cols]


def save_no_header_csv(df: pd.DataFrame, out_path: str) -> None:
    df.to_csv(out_path, index=False, header=False)


def main():
    # =========================
    # 3) Session SageMaker
    # =========================
    check_input_file(LOCAL_CSV)

    session = sagemaker.Session()
    region = boto3.Session().region_name
    bucket = session.default_bucket()

    try:
        role = sagemaker.get_execution_role()
    except Exception as e:
        fail(
            "Không lấy được SageMaker execution role. "
            "Hãy chạy script này trong SageMaker Notebook/Studio, "
            f"hoặc tự truyền role nếu cần. Chi tiết: {e}"
        )

    log(f"Region: {region}")
    log(f"Bucket: {bucket}")
    log(f"Role: {role}")

    # =========================
    # 4) Đọc và xử lý dữ liệu
    # =========================
    log(f"Đọc dữ liệu từ {LOCAL_CSV}")
    raw_df = pd.read_csv(LOCAL_CSV)

    df = preprocess_dataframe(raw_df)
    log(f"Kích thước sau tiền xử lý: {df.shape}")

    train_df, val_df, test_df = split_data(df)

    train_df = reorder_for_sagemaker(train_df, TARGET_COL)
    val_df = reorder_for_sagemaker(val_df, TARGET_COL)
    test_df = reorder_for_sagemaker(test_df, TARGET_COL)

    log(f"Train shape: {train_df.shape}")
    log(f"Validation shape: {val_df.shape}")
    log(f"Test shape: {test_df.shape}")

    feature_cols = [c for c in train_df.columns if c != TARGET_COL]
    log(f"Feature columns: {feature_cols}")

    # Lưu metadata feature để dùng lúc inference
    metadata = {
        "target_col": TARGET_COL,
        "feature_cols": feature_cols,
        "category_mappings": {
            "Fuel_Type": {"Petrol": 0, "Diesel": 1, "CNG": 2},
            "Seller_Type": {"Dealer": 0, "Individual": 1},
            "Transmission": {"Manual": 0, "Automatic": 1},
        },
        "current_year_for_car_age": CURRENT_YEAR,
    }
    with open("model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # =========================
    # 5) Ghi file local
    # =========================
    train_local = "train.csv"
    val_local = "validation.csv"
    test_local = "test.csv"

    save_no_header_csv(train_df, train_local)
    save_no_header_csv(val_df, val_local)
    save_no_header_csv(test_df, test_local)

    log("Đã lưu train.csv, validation.csv, test.csv")

    # =========================
    # 6) Upload S3
    # =========================
    train_s3_uri = session.upload_data(
        path=train_local,
        bucket=bucket,
        key_prefix=f"{S3_PREFIX}/train"
    )
    val_s3_uri = session.upload_data(
        path=val_local,
        bucket=bucket,
        key_prefix=f"{S3_PREFIX}/validation"
    )
    test_s3_uri = session.upload_data(
        path=test_local,
        bucket=bucket,
        key_prefix=f"{S3_PREFIX}/test"
    )
    metadata_s3_uri = session.upload_data(
        path="model_metadata.json",
        bucket=bucket,
        key_prefix=f"{S3_PREFIX}/metadata"
    )

    log(f"Train S3 URI: {train_s3_uri}")
    log(f"Validation S3 URI: {val_s3_uri}")
    log(f"Test S3 URI: {test_s3_uri}")
    log(f"Metadata S3 URI: {metadata_s3_uri}")

    # =========================
    # 7) Lấy built-in image XGBoost
    # =========================
    container = image_uris.retrieve(
        framework="xgboost",
        region=region,
        version=XGBOOST_VERSION,
    )
    log(f"XGBoost container: {container}")

    # =========================
    # 8) Tạo estimator
    # =========================
    xgb = Estimator(
        image_uri=container,
        role=role,
        instance_count=INSTANCE_COUNT,
        instance_type=INSTANCE_TYPE,
        output_path=f"s3://{bucket}/{S3_PREFIX}/output",
        sagemaker_session=session,
    )

    # Hyperparameters phổ biến cho XGBoost regression
    xgb.set_hyperparameters(
        objective="reg:squarederror",
        num_round=300,
        max_depth=5,
        eta=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=3,
        gamma=0.0,
        eval_metric="rmse",
    )

    # =========================
    # 9) Train
    # =========================
    log("Bắt đầu train SageMaker built-in XGBoost...")
    xgb.fit(
        inputs={
            "train": TrainingInput(
                s3_data=train_s3_uri,
                content_type="text/csv"
            ),
            "validation": TrainingInput(
                s3_data=val_s3_uri,
                content_type="text/csv"
            ),
        },
        logs=True,
    )

    log("Train xong.")
    log(f"Model artifact: {xgb.model_data}")
    log("Bạn có thể deploy tiếp bằng xgb.deploy(...) trong notebook khác hoặc script khác.")


if __name__ == "__main__":
    main()