import numpy as np
import pandas as pd
import yaml

import sys
import time
import os
import json
import logging
import argparse

def logging_setup(log_file):
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        required_keys = ['seed', 'window', 'version']
        for key in required_keys:
            if key not in config:
                raise KeyError(f"Missing required configuration key: {key}")
        return config
    except Exception as e:
        raise RuntimeError(f"Error loading configuration: {e}")
    
def load_dataset(dataset_path):
    try:
        df = pd.read_csv(dataset_path, encoding="utf-8-sig")

        if len(df.columns) == 1:
            df = pd.read_csv(
                dataset_path,
                sep=",",
                encoding="utf-8-sig",
                quoting=3  
            )

        df.columns = df.columns.str.strip().str.lower()

        if df.empty:
            raise ValueError("Dataset is empty.")
        if "close" not in df.columns:
            raise KeyError("Dataset must contain 'close' column for processing.")
        return df
    except FileNotFoundError:
        raise RuntimeError(f"Dataset file not found: {dataset_path}")
    except pd.errors.ParserError:
        raise RuntimeError(f"Error parsing dataset file: {dataset_path}")
    except Exception as e:
        raise RuntimeError(f"Other error loading dataset: {e}")
    
def signal_computation(df, window):
    df['rolling_mean'] = df['close'].rolling(window=window).mean()
    df['signal'] = (df['close'] > df['rolling_mean']).astype(int)
    return df
def save_metrics(metrics, output_path):
    try:
        with open(output_path, 'w') as file:
            json.dump(metrics, file, indent=2)
    except Exception as e:
        raise RuntimeError(f"Error saving metrics: {e}")
    
def main():
    parser = argparse.ArgumentParser(description="Run the signal computation pipeline.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--log-file", required=True)

    args=parser.parse_args()
    logging_setup(args.log_file)
    start_time = time.time()
    try:
        logging.info("Started Job")
        config = load_config(args.config)
        seed = config['seed']
        window=config['window']
        version=config['version']

        np.random.seed(seed)
        logging.info(f"Configuration loaded: Seed={seed}, Window={window}, Version={version}")

        df= load_dataset(args.input)
        logging.info(f"Dataset loaded with {len(df)} rows.")

        df= signal_computation(df, window)
        valid_rows=df['signal'].dropna()
        signal_rate= valid_rows.mean()
        latency_ms=int((time.time() - start_time) * 1000)

        metrics = {
            "version": version,
            "rows_processed" : len(df),
            "metric": signal_rate,
            "value" :  round(float(signal_rate),4),
            "latency_ms": latency_ms,
            "seed": seed,
            "status" : "success"
        }

        logging.info(f"Metrics computation completed: {metrics}")
        save_metrics(metrics, args.output)
        print(json.dumps(metrics, indent=2))
        logging.info("Job completed successfully.")
        sys.exit(0)

    except Exception as e:
        latency_ms=int((time.time() - start_time) * 1000)
        error_metrics = {
            "version": "v1",
            "status": "error",
            "error_message": str(e)
        }

        save_metrics(error_metrics, args.output)
        logging.error(str(e))
        print(json.dumps(error_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()